from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
import logging

from artelie.serializers.user import (
    UserSerializer, UserDetailSerializer, UserCreateSerializer,
    UserUpdateSerializer, UserPasswordChangeSerializer, PublicUserSerializer
)
from artelie.permissions import IsOwnerOrAdmin  # Criar esta permission

logger = logging.getLogger(__name__)
User = get_user_model()


class UserRateThrottle(UserRateThrottle):
    """Throttling personalizado para operações de usuário."""
    scope = 'user_operations'


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gerenciamento de usuários.
    
    Funcionalidades:
    - CRUD completo com permissões diferenciadas
    - Filtros e busca avançada  
    - Throttling para proteção
    - Logging de auditoria
    - Ações personalizadas (trocar senha, etc.)
    """
    
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'is_active': ['exact'],
        'is_verified': ['exact'], 
        'is_staff': ['exact'],
        'created_at': ['gte', 'lte', 'exact', 'year', 'month'],
    }
    search_fields = ['username', 'email', 'full_name']
    ordering_fields = ['created_at', 'username', 'email', 'last_login']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Queryset com filtros de segurança e otimizações.
        """
        queryset = User.objects.select_related('address')
        
        # Filtros baseados no usuário atual
        user = self.request.user
        
        if not user.is_authenticated:
            # Usuários não autenticados não veem nada
            return queryset.none()
        
        elif user.is_staff:
            # Staff vê todos os usuários ativos
            queryset = queryset.filter(is_active=True)
        else:
            # Usuários normais veem apenas a si mesmos
            queryset = queryset.filter(id=user.id)
        
        # Otimização: prefetch relacionamentos se necessário
        if self.action == 'list':
            queryset = queryset.only(
                'id', 'username', 'email', 'full_name', 
                'is_active', 'is_verified', 'created_at'
            )
        
        return queryset
    
    def get_permissions(self):
        """
        Permissões diferenciadas por ação.
        """
        if self.action == 'create':
            # Apenas admin pode criar usuários via API
            permission_classes = [IsAdminUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Usuário ou admin
            permission_classes = [IsOwnerOrAdmin]
        elif self.action == 'list':
            # Admin para listar todos, usuário autenticado para ver a si mesmo
            permission_classes = [IsAuthenticated]
        elif self.action in ['change_password', 'deactivate_account']:
            # Apenas o próprio usuário ou admin
            permission_classes = [IsOwnerOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """
        Serializers específicos por ação.
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer  
        elif self.action in ['update', 'partial_update']:
            # Se admin pode usar serializer completo, senão apenas campos básicos
            if self.request.user.is_staff:
                return UserSerializer
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return UserPasswordChangeSerializer
        elif self.action == 'list' and not self.request.user.is_staff:
            # Usuários não-admin veem versão pública
            return PublicUserSerializer
        
        return UserSerializer
    
    def perform_create(self, serializer):
        """Auditoria e logging na criação."""
        user = serializer.save()
        logger.info(
            f"User created: {user.username} ({user.email}) by {self.request.user}",
            extra={
                'user_id': str(user.id),
                'created_by': str(self.request.user.id),
                'ip': self.get_client_ip()
            }
        )
    
    def perform_update(self, serializer):
        """Auditoria e logging na atualização."""
        old_instance = self.get_object()
        user = serializer.save()
        
        # Log das alterações específicas
        changes = []
        for field in ['username', 'email', 'full_name', 'is_active', 'is_staff']:
            old_value = getattr(old_instance, field, None)
            new_value = getattr(user, field, None)
            if old_value != new_value:
                changes.append(f"{field}: {old_value} → {new_value}")
        
        if changes:
            logger.info(
                f"User updated: {user.username} - Changes: {', '.join(changes)} by {self.request.user}",
                extra={
                    'user_id': str(user.id),
                    'updated_by': str(self.request.user.id),
                    'changes': changes,
                    'ip': self.get_client_ip()
                }
            )
    
    def perform_destroy(self, instance):
        """
        Soft delete ao invés de exclusão física.
        """
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        
        logger.warning(
            f"User deactivated: {instance.username} by {self.request.user}",
            extra={
                'user_id': str(instance.id),
                'deactivated_by': str(self.request.user.id),
                'ip': self.get_client_ip()
            }
        )
    
    @action(detail=True, methods=['post'], url_path='change-password')
    def change_password(self, request, pk=None):
        """
        Ação para trocar senha do usuário.
        """
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verificar se é o próprio usuário ou admin
        if user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Você só pode alterar sua própria senha.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer.save()
        
        # Log da troca de senha
        logger.info(
            f"Password changed for user: {user.username} by {request.user}",
            extra={
                'user_id': str(user.id),
                'changed_by': str(request.user.id),
                'ip': self.get_client_ip()
            }
        )
        
        return Response({
            'message': 'Senha alterada com sucesso.',
            'timestamp': timezone.now()
        })
    
    @action(detail=True, methods=['post'], url_path='deactivate-account')
    def deactivate_account(self, request, pk=None):
        """
        Permite que usuários desativem suas próprias contas.
        """
        user = self.get_object()
        
        # Apenas o próprio usuário ou admin
        if user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Você só pode desativar sua própria conta.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Não permitir que admin desative a própria conta
        if user.is_staff and user == request.user:
            return Response(
                {'error': 'Administradores não podem desativar suas próprias contas.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = False
        user.save(update_fields=['is_active'])
        
        logger.warning(
            f"Account self-deactivated: {user.username}",
            extra={
                'user_id': str(user.id),
                'ip': self.get_client_ip()
            }
        )
        
        return Response({
            'message': 'Conta desativada com sucesso.',
            'deactivated_at': timezone.now()
        })
    
    @action(detail=False, methods=['get'], url_path='me')
    def current_user(self, request):
        """
        Retorna informações do usuário atual.
        """
        serializer = UserDetailSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='stats', permission_classes=[IsAdminUser])
    def user_stats(self, request):
        """
        Estatísticas de usuários (apenas para admins).
        """
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
            'staff_users': User.objects.filter(is_staff=True).count(),
            'users_today': User.objects.filter(created_at__date=timezone.now().date()).count(),
        }
        
        return Response(stats)
    
    def get_client_ip(self):
        """
        Obtém IP do cliente para logging.
        """
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

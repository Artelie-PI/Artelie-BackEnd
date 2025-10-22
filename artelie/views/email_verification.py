from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging
import uuid

logger = logging.getLogger(__name__)
User = get_user_model()


class EmailVerificationView(APIView):
    """
    View para verificar email do usuário através do token.
    """
    permission_classes = [AllowAny]

    def get(self, request, token):
        """
        Verifica o token e ativa a conta do usuário.
        """
        try:
            # Buscar usuário pelo token
            user = User.objects.get(verification_token=token)
            
            # Verificar se token ainda é válido
            if not user.is_verification_token_valid():
                logger.warning(
                    f"Token expirado para usuário: {user.email}",
                    extra={'user_id': str(user.id)}
                )
                return Response({
                    'error': 'Token de verificação expirado.',
                    'message': 'Solicite um novo email de verificação.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Ativar usuário
            user.is_active = True
            user.is_verified = True
            user.verification_token = None
            user.verification_token_created_at = None
            user.save(update_fields=[
                'is_active', 'is_verified', 
                'verification_token', 'verification_token_created_at'
            ])
            
            logger.info(
                f"Email verificado com sucesso: {user.email}",
                extra={'user_id': str(user.id)}
            )
            
            return Response({
                'message': 'Email verificado com sucesso! Sua conta está ativa.',
                'user_id': str(user.id),
                'email': user.email
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            logger.warning(
                f"Token inválido recebido: {token[:8]}...",
                extra={'token_prefix': token[:8]}
            )
            return Response({
                'error': 'Token de verificação inválido.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(
                f"Erro na verificação de email: {str(e)}",
                extra={'error_type': type(e).__name__},
                exc_info=True
            )
            return Response({
                'error': 'Erro ao verificar email. Tente novamente mais tarde.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendVerificationEmailView(APIView):
    """
    View para reenviar email de verificação.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Reenvia email de verificação para o usuário.
        """
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': 'Email é obrigatório.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email.lower())
            
            # Verificar se já está verificado
            if user.is_verified:
                return Response({
                    'message': 'Este email já está verificado.'
                }, status=status.HTTP_200_OK)
            
            # Gerar novo token
            user.verification_token = str(uuid.uuid4())
            user.verification_token_created_at = timezone.now()
            user.save(update_fields=['verification_token', 'verification_token_created_at'])
            
            # Aqui você chamaria a função de envio de email
            # Para simplificar, apenas log
            logger.info(
                f"Email de verificação reenviado para: {user.email}",
                extra={'user_id': str(user.id)}
            )
            
            return Response({
                'message': 'Email de verificação reenviado com sucesso.'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Por segurança, não revelar se email existe ou não
            return Response({
                'message': 'Se o email existir, você receberá um email de verificação.'
            }, status=status.HTTP_200_OK)

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
import re

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    """Serializer base com validações comuns."""
    
    def validate_email(self, value):
        """Validação do email."""
        value = value.lower().strip()
        
        # Verifica se o email existe (menos o próprio usuário na edição)
        queryset = User.objects.filter(email=value)
        if self.instance:  # ✅ CORRIGIDO (era self.isinstance)
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("Este email já está em uso.")
        
        return value
    
    def validate_username(self, value):
        """Validação do username."""
        value = value.lower().strip()
        
        if len(value) < 3:
            raise serializers.ValidationError("O nome de usuário deve ter pelo menos 3 caracteres")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "O nome de usuário só pode conter letras, números e underline."
            )
        
        # Verifica se o username existe (menos o próprio usuário na edição)
        queryset = User.objects.filter(username=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        
        return value


class UserSerializer(BaseUserSerializer):
    """Serializer para CRUD e usado pelo adm"""
    full_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    
    class Meta:
        model = User  # ✅ ADICIONADO
        fields = [
            'id', 'username', 'email', 'full_name', 
            'is_active', 'is_verified', 'is_staff',
            'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_login',
            'is_verified'
        ]
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'username': {'required': True, 'allow_blank': False},
        }
    
    def to_representation(self, instance):
        """Representação personalizada do usuário."""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Esconde campos sensíveis se não for staff
        if (request and not request.user.is_staff and request.user != instance):
            sensitive_fields = ['is_active', 'is_staff', 'last_login']
            for field in sensitive_fields:
                data.pop(field, None)
        
        return data


class UserDetailSerializer(UserSerializer):  # ✅ CORRIGIDO: herda de UserSerializer
    """Detalha informações individuais e infos adicionais"""
    address = serializers.SerializerMethodField()
    full_name_display = serializers.SerializerMethodField()
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['address', 'full_name_display']
    
    def get_address(self, obj):
        """Retorna o endereço se existir"""
        if obj.address:
            from artelie.serializers.address import AddressSerializer
            return AddressSerializer(obj.address).data
        return None
    
    def get_full_name_display(self, obj):
        """Retorna o nome formatado"""
        return obj.get_full_name()


class UserCreateSerializer(BaseUserSerializer):
    """Criação de user por adm"""
    password = serializers.CharField(
        min_length=8, 
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}, 
        help_text="Senha do usuário. Deve ter pelo menos 8 caracteres."
    )
    password_confirm = serializers.CharField(
        min_length=8, 
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}, 
        help_text="Confirmação da senha."
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'full_name', 
            'password', 'password_confirm',
            'is_active', 'is_staff'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'full_name': {'required': False},
        }
    
    def validate_password(self, value):
        """Validação da senha usando validadores do Django."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validação cross-field."""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': "As senhas não estão iguais."
            })
        
        return attrs
    
    def create(self, validated_data):
        """Cria user"""
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        
        user = User.objects.create_user(password=password, **validated_data)
        user.set_password(password)
        user.save()
        
        return user


class UserUpdateSerializer(BaseUserSerializer):
    """Serializer para atualização de usuário"""
    
    class Meta:
        model = User
        fields = ['username', 'email', 'full_name']
        extra_kwargs = {
            'email': {'required': False},
            'username': {'required': False},
            'full_name': {'required': False},
        }
    
    def validate(self, attrs):
        """Validação para evitar alteração desnecessária"""
        if not attrs:
            raise serializers.ValidationError("Nenhum dado fornecido para atualização.")
        return attrs


class UserPasswordChangeSerializer(serializers.Serializer):
    """Serializer para troca de senha de usuários autenticados."""
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Senha atual do usuário."
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Nova senha (mínimo 8 caracteres)."
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirmação da nova senha."
    )
    
    def validate_old_password(self, value):
        """Verifica se a senha atual está correta."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value
    
    def validate_new_password(self, value):
        """Validação da nova senha."""
        try:
            validate_password(value, user=self.context['request'].user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validação cross-field."""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        old_password = attrs.get('old_password')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'As senhas não coincidem.'
            })
        
        if old_password == new_password:
            raise serializers.ValidationError({
                'new_password': 'A nova senha deve ser diferente da atual.'
            })
        
        return attrs
    
    def save(self):
        """Atualiza a senha do usuário."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user


class PublicUserSerializer(serializers.ModelSerializer):
    """Serializer para informações públicas do usuário."""
    full_name_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name_display']
    
    def get_full_name_display(self, obj):
        return obj.get_full_name()

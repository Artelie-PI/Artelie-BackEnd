from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
import re

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de novos usuários.
    Inclui validações robustas de segurança.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Mínimo 8 caracteres com letra maiúscula, minúscula, número e caractere especial"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirmação da senha"
    )
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True, min_length=3, max_length=50)
    full_name = serializers.CharField(required=False, allow_blank=True, max_length=150)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'full_name']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate_email(self, value):
        """
        Validação de email único e formatação.
        BENEFÍCIO: Previne duplicação e normaliza formato.
        """
        value = value.lower().strip()
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Um usuário com este email já existe."
            )
        
        return value

    def validate_username(self, value):
        """
        Validação de username.
        BENEFÍCIO: Garante padrão seguro e único.
        """
        value = value.lower().strip()
        
        # Comprimento mínimo
        if len(value) < 3:
            raise serializers.ValidationError(
                "Username deve ter pelo menos 3 caracteres."
            )
        
        # Apenas caracteres alfanuméricos e underscore
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise serializers.ValidationError(
                "Username pode conter apenas letras, números e underscore."
            )
        
        # Verificar se já existe
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Este username já está em uso."
            )
        
        # Evitar usernames reservados
        reserved_usernames = [
            'admin', 'root', 'superuser', 'administrator', 
            'system', 'support', 'help', 'api', 'www'
        ]
        if value.lower() in reserved_usernames:
            raise serializers.ValidationError(
                "Este username não pode ser usado."
            )
        
        return value

    def validate_password(self, value):
        """
        Validação avançada de senha usando validadores do Django.
        BENEFÍCIO: Força senhas fortes, previne senhas comuns.
        """
        try:
            # Usa os validadores configurados em AUTH_PASSWORD_VALIDATORS
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        # Validações adicionais personalizadas
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError(
                "Senha deve conter pelo menos uma letra maiúscula."
            )
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError(
                "Senha deve conter pelo menos uma letra minúscula."
            )
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError(
                "Senha deve conter pelo menos um número."
            )
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError(
                "Senha deve conter pelo menos um caractere especial."
            )
        
        return value

    def validate(self, attrs):
        """
        Validação cross-field.
        BENEFÍCIO: Garante consistência entre campos relacionados.
        """
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        username = attrs.get('username')
        email = attrs.get('email')
        
        # Confirmar senhas coincidem
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'As senhas não coincidem.'
            })
        
        # Senha não pode ser similar ao username
        if password.lower() in username.lower() or username.lower() in password.lower():
            raise serializers.ValidationError({
                'password': 'Senha não pode ser similar ao nome de usuário.'
            })
        
        # Senha não pode conter partes do email
        email_local = email.split('@')[0]
        if email_local.lower() in password.lower():
            raise serializers.ValidationError({
                'password': 'Senha não pode conter partes do email.'
            })
        
        return attrs

    def create(self, validated_data):
        """
        Criação do usuário com segurança.
        BENEFÍCIO: Usuário inativo até verificar email.
        """
        # Remover confirmação de senha
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        
        # Criar usuário inativo
        user = User.objects.create_user(
            **validated_data,
            is_active=False  # Inativo até verificar email
        )
        user.set_password(password)
        user.save()
        
        return user

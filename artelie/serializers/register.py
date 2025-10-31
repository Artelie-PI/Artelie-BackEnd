from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
import re

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de novos usuários.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Mínimo 8 caracteres"
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
        """Validação de email único."""
        value = value.lower().strip()
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Um usuário com este email já existe.")
        
        return value

    def validate_username(self, value):
        """Validação de username."""
        value = value.lower().strip()
        
        if len(value) < 3:
            raise serializers.ValidationError("Username deve ter pelo menos 3 caracteres.")
        
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise serializers.ValidationError("Username pode conter apenas letras, números e underscore.")
        
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este username já está em uso.")
        
        reserved_usernames = ['admin', 'root', 'superuser', 'administrator', 'system', 'support', 'help', 'api', 'www']
        if value.lower() in reserved_usernames:
            raise serializers.ValidationError("Este username não pode ser usado.")
        
        return value

    def validate_password(self, value):
        """Validação de senha - SEM regex restritivo."""
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
                'password_confirm': 'As senhas não coincidem.'
            })
        
        return attrs

    def create(self, validated_data):
        """Criação do usuário."""
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        return user

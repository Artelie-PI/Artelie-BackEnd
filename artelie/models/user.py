from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta
import uuid
from .address import Address

class UserManager(BaseUserManager):
    """
    Manager personalizado para o modelo User.
    Gerencia a criação de usuários normais e superusuários.
    """
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Cria e salva um usuário com o username, email e senha fornecidos.
        """
        if not email:
            raise ValueError('O email é obrigatório')
        if not username:
            raise ValueError('O nome de usuário é obrigatório')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Cria usuário comum (não staff, não superuser).
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', False) # ele vai ficar inativo até confirmar o email
        return self._create_user(username, email, password, **extra_fields)
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """ Cria superuser com permissoes administrativas. """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) # superuser sempre ativo 

        if extra_fields.get('is_staff') is not True:
            raise ValueError ('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError ('Superuser must have is_superuser=True')
        
        return self._create_user(username, email, password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuário personalizado usando AbstractBaseuser.
    Utiliza email como campo de autenticação principal.
    """

    #validador para username (só letras, número e underscore)
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_]+$',
        message='Username só pode conter letras, números e underlines (_).'
    )

    #campos básicos de usuário
    id = models.UUIDField(primary_key=True, default==uuid.uuid4, editable=False, help_text='Identificador único do usuário. (UUID)')
    username = models.CharField(max_length=50, unique=True, validators=[username_validator], help_text="Nome de usuário único. (3-50 caracteres)")
    email = models.EmailField(max_length=254, unique=True, help_text="Endereço de email único do usuário.")
    full_name = models.CharField(max_length=150, blank=True, help_text="Nome completo do usuário.")

    #campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data e hora de criação do usuário.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Data e hora da última atualização do usuário.")
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, help_text="Último IP de login do usuário.")

    #campos de status
    is_active = models.BooleanField(default=False, help_text="Indica se o usuário está ativo.")
    is_staff = models.BooleanField(default=False, help_text="Indica se o usuário pode acessar o admin site.")
    is_verified = models.BooleanField(default=False, help_text="Indica se o email do usuário foi verificado.")


    #campo de verificação de email
    verification_token = models.CharField(max_length=100, blank=True, null=True, help_text="Token para verificação de email.")
    verification_token_created_at = models.DateTimeField(null=True, blank=True, help_text="Data e hora de criação do token de verificação.")

    #segurança
    failed_login_attempts = models.PositiveIntegerField(default=0, help_text="Número de tentativas de login falhas.")
    locked_until = models.DateTimeField(null=True, blank=True, help_text="Data e hora até a qual o usuário está bloqueado.")

    #relacionamento com endereço
    address = models.OneToOneField(Address, on_delete=models.PROTECT, null=True, blank=True, related_name='user')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'artelie_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['is_active', 'is_verified']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"

    def clean(self):
        """Validação adicional no nível da model."""
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
        self.username = self.username.lower() if self.username else ''

    def save(self, *args, **kwargs):
        """Sobrescrever save para aplicar save"""
        self.clean()
        super().save(*args, **kwargs)

    def is_verification_token_valid(self):
        """Vereifica se o token de verificação ainda é válido (24 horas)"""
        if not self.verification_token_created_at:
            return False
        expiration_time = self.verification_token_created_at + timedelta(hours=24)
        return timezone.now() < expiration_time
    

    def is_account_locked(self):
        """Verifica se a conta está bloqueada por tentativas excessivas de login"""
        if self.locked_until:
            return timezone.now() < self.locked_until
        return False
    
    def reset_failed_logins(self):
        """Reseta o contador de tentativas falhas de login"""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def increment_failed_attempts(self):
        """contador de tentativas falhas de login e bloqueia a conta se necessário"""
        self.failed_login_attempts += 1

        #bloqueia a conta por 15 minutos após 5 tentativas falhas
        if self.failed_login_attempts >= 5:
            self.locked_until = timezone.now() + timedelta(minutes=15)

        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def get_full_name(self):
        """Retorna o nome completo do usuário."""
        return self.full_name.strip() if self.full_name else self.username
    
    def get_short_name(self):
        """retorna o nome curto do user."""
        if self.full_name:
            return self.full_name.split()[0]
        return self.username
        

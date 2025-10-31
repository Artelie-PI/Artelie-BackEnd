from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from django.utils import timezone
import logging
import uuid
import os


from artelie.serializers.register import RegisterSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class RegistrationRateThrottle(AnonRateThrottle):
    """
    Throttling específico para registro - mais restritivo.
    BENEFÍCIO: Previne spam e bots automatizados.
    """
    scope = 'registration'


class RegisterView(generics.CreateAPIView):
    """
    View para registro de novos usuários com medidas de segurança avançadas.
    
    Funcionalidades:
    - Rate limiting para prevenir spam
    - Validação de força de senha
    - Envio de email de verificação
    - Logging de auditoria
    - Tratamento de erros robusto
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegistrationRateThrottle]

    def create(self, request, *args, **kwargs):
        """
        Processo de registro com validações de segurança.
        BENEFÍCIO: Fluxo completo e seguro de registro.
        """
        try:
            # Log da tentativa de registro (sem dados sensíveis)
            client_ip = self.get_client_ip(request)
            logger.info(
                f"Tentativa de registro de IP: {client_ip}",
                extra={'ip': client_ip, 'timestamp': timezone.now()}
            )
            
            # Validação do serializer
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Criar usuário (já vem inativo do serializer)
            user = self.perform_create(serializer)
            
            # Gerar e enviar token de verificação
            verification_sent = self.send_verification_email(user, request)
            
            # Log de sucesso (sem dados sensíveis)
            logger.info(
                f"Usuário registrado com sucesso: {user.email}",
                extra={
                    'user_id': str(user.id),
                    'email': user.email,
                    'ip': client_ip,
                    'verification_sent': verification_sent
                }
            )
            
            headers = self.get_success_headers(serializer.data)
            return Response({
                "message": "Usuário registrado com sucesso! Verifique seu email para ativar a conta.",
                "user_id": str(user.id),
                "email": user.email,
                "email_verification_sent": verification_sent,
                "next_step": "Verifique sua caixa de entrada e spam para o email de ativação."
            }, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            # Log de erro sem expor dados sensíveis
            logger.error(
                f"Erro no registro: {str(e)}",
                extra={
                    'ip': self.get_client_ip(request),
                    'error_type': type(e).__name__
                },
                exc_info=True
            )
            
            # Não expor detalhes internos ao usuário
            return Response({
                "error": "Erro ao processar registro. Tente novamente mais tarde."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        """
        Criação do usuário com lógica adicional.
        BENEFÍCIO: Centraliza lógica de criação.
        """
        user = serializer.save()
        return user

    def send_verification_email(self, user, request):
        """
        Envia email de verificação com token seguro.
        BENEFÍCIO: Garante que email é válido antes de ativar conta.
        """
        try:
            # Gerar token de verificação único
            verification_token = str(uuid.uuid4())
            user.verification_token = verification_token
            user.verification_token_created_at = timezone.now()
            user.save(update_fields=['verification_token', 'verification_token_created_at'])
            
            # URL de verificação
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
            verification_url = f"{frontend_url}/verify-email/{verification_token}"
            
            # Renderizar email HTML
            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #192EB1;">Bem-vindo à Artelie, {user.username}!</h2>
                    <p>Obrigado por se cadastrar. Para ativar sua conta, clique no botão abaixo:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Ativar minha conta</a>
                    </div>
                    <p>Ou copie e cole este link no seu navegador:</p>
                    <p style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; word-break: break-all;">{verification_url}</p>
                    <p><strong>Este link expira em 24 horas.</strong></p>
                    <p style="color: #666; font-size: 0.9em;">Se você não se cadastrou, ignore este email.</p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="color: #999; font-size: 0.8em;">Atenciosamente,<br>Equipe Artelie</p>
                </div>
            </body>
            </html>
            """
            
            # Versão texto simples
            plain_message = f"""
            Bem-vindo à Artelie, {user.username}!
            
            Obrigado por se cadastrar. Para ativar sua conta, acesse o link abaixo:
            
            {verification_url}
            
            Este link expira em 24 horas.
            
            Se você não se cadastrou, ignore este email.
            
            Atenciosamente,
            Equipe Artelie
            """
            
            # Envio do email
            send_mail(
                subject='Confirme seu email - Artelie',
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(
                f"Email de verificação enviado para: {user.email}",
                extra={'user_id': str(user.id), 'email': user.email, 'url': verification_url}
            )
            
            return True
            
        except Exception as e:
            logger.error(
                f"Erro ao enviar email de verificação: {str(e)}",
                extra={
                    'user_id': str(user.id),
                    'email': user.email,
                    'error_type': type(e).__name__
                },
                exc_info=True
            )
            return False


    def get_client_ip(self, request):
        """
        Obtém IP do cliente para logging e segurança.
        BENEFÍCIO: Rastreabilidade e detecção de abusos.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip

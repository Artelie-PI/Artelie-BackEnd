from rest_framework_simplejwt.views import TokenObtainPairView
from artelie.serializers.token import EmailTokenObtainPairSerializer

class EmailTokenObtainPairView(TokenObtainPairView):
    """
    View customizada para aceitar EMAIL no login JWT.
    """
    serializer_class = EmailTokenObtainPairSerializer

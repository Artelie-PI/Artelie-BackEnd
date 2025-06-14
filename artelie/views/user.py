from rest_framework import viewsets

from artelie.models import User
from artelie.serializers.user import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar usuários.
    Permite listar, criar, atualizar e excluir usuários.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    
    def get_queryset(self):
        return self.queryset.filter(is_active=True)  # Exemplo de filtro para retornar apenas usuários ativos
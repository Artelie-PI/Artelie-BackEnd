from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from artelie.models.user import User
from artelie.serializers.register import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"message": "Usuário criado com sucesso!"}, status=status.HTTP_201_CREATED, headers=headers)

from rest_framework import generics
from artelie.serializers.register import RegisterSerializer
from artelie.models.user import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
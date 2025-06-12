from rest_framework import serializers
from artelie.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'created_at', 'is_active', 'is_staff']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'username': {'required': True, 'max_length': 50},
            'email': {'required': True, 'max_length': 120, 'allow_blank': False},
            'full_name': {'required': False, 'max_length': 100, 'allow_blank': True},
        }
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username'],
                message="A user with this username already exists."
            ),
            serializers.UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['email'],
                message="A user with this email already exists."
            )
        ]
from rest_framework import serializers
from artelie.models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'required': True, 'max_length': 255},
            'description': {'required': False, 'allow_blank': True, 'max_length': 500},
        }
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=['name'],
                message="A category with this name already exists."
            )
        ]
from rest_framework import serializers
from artelie.models import Category
from artelie.serializers.product import ProductSerializer


class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True, source='product_set')

    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at', 'products']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'required': True, 'max_length': 255},
        }
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=['name'],
                message="A category with this name already exists.",
            )
        ]

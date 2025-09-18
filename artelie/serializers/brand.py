from rest_framework import serializers
from artelie.models import Brand

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'
        read_only_fields = ['id', 'updated_at']
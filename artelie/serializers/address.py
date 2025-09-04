from rest_framework import serializers
from artelie.models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
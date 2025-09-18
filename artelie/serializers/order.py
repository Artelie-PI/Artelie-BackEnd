from rest_framework.serializers import ModelSerializer, CharField
from artelie.models import Order

class OrderSerializer(ModelSerializer):
    user = CharField(source='user.email', read_only=True)
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('ordered_at',)
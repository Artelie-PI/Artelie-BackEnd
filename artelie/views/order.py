from rest_framework.viewsets import ModelViewSet

from artelie.models import Order
from rest_framework.permissions import IsAuthenticated
from artelie.serializers import OrderSerializer

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = []
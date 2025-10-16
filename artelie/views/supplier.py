from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from artelie.models import Supplier
from artelie.serializers import SupplierSerializer

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    depth = 1
    serializer_class = SupplierSerializer
    permission_classes = []
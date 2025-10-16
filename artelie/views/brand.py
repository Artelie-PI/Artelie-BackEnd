from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from artelie.models import Brand
from artelie.serializers import BrandSerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = []
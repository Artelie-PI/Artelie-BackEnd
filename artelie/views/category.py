from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from artelie.models import Category
from artelie.serializers import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = []  # Adjust permissions as needed
    lookup_field = 'slug'  # Assuming 'slug' is a field in the Category model


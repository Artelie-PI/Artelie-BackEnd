# views/category.py
from rest_framework import viewsets
from artelie.models import Category
from artelie.serializers import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

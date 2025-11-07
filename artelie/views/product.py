from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from artelie.models import Product
from artelie.serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = []
    # Habilita filtros simples por categoria, marca e fornecedor
    filterset_fields = ["category", "brand", "supplier"]
    # Permite busca por nome e descrição (?search=texto)
    search_fields = ["name", "description"]
    # Permite ordenação por nome, preço e data de criação (?ordering=price ou -price)
    ordering_fields = ["name", "price", "created_at"]
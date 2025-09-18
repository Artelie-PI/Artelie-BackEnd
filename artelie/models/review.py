from django.db import models
from artelie.models import Product, User

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # Exemplo: 1 a 5 estrelas
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  # Um usuário só pode avaliar um produto uma vez

    def __str__(self):
        return f"{self.user.username} avaliou {self.product.name} ({self.rating} estrelas)"
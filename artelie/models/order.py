from django.db import models
from artelie.models import User, Product

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    ordered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ('PENDENTE', 'Pendente'),
            ('ENVIADO', 'Enviado'),
            ('ENTREGUE', 'Entregue'),
            ('CANCELADO', 'Cancelado'),
        ],
        default='PENDENTE'
    )

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"
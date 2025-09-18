from django.db import models
from artelie.models import User, Product


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    ordered_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)   # novo
    updated_at = models.DateTimeField(auto_now=True)       # novo
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

    @property
    def total_amount(self):
        """Soma o preço total dos itens do pedido"""
        return sum(item.product.price * item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"

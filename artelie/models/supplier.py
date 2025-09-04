from django.db import models
from .address import Address

class Supplier(models.Model):
    name = models.CharField(max_length=100, unique=True)
    contact_email = models.EmailField(max_length=120, unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.OneToOneField(Address, on_delete=models.PROTECT, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Suppliers"
        ordering = ['name']
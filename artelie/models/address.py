from django.db import models


class Address(models.Model):
    street = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.zip_code}"

    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['state', 'city', 'street']
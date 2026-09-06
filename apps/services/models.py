from django.db import models

from apps.services.fields import EncryptedTextField


# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=200, unique=True)
    url = models.URLField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    api_key = EncryptedTextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

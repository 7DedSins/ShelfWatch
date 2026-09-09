from django.db import models

from apps.services.fields import EncryptedTextField


# Create your models here.
class Service(models.Model):
    class Kind(models.TextChoices):
        # Stored value, admin label. Registry keys are the values.
        KAVITA = "kavita", "Kavita"
        LANRARAGI = "lanraragi", "LANraragi"

    name = models.CharField(max_length=200, unique=True)
    url = models.URLField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    api_key = EncryptedTextField(blank=True)
    kind = models.CharField(max_length=32, choices=Kind.choices, default=Kind.KAVITA)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

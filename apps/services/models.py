from django.core.validators import MinValueValidator
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
    # NULL = never polled (not the same as False = polled and failed).
    last_health_ok = models.BooleanField(null=True, blank=True)
    last_polled_at = models.DateTimeField(null=True, blank=True)
    # Due-ness is this column vs last_polled_at, not a Beat crontab per service.
    # PositiveIntegerField allows 0; MinValueValidator is full_clean/admin only.
    poll_interval_seconds = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

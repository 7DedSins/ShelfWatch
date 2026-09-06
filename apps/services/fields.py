from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models


class EncryptedTextField(models.TextField):
    def _fernet(self):
        return Fernet(settings.FIELD_ENCRYPTION_KEY.encode())

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if not value:
            return value
        return self._fernet().encrypt(value.encode()).decode()

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        return super().to_python(self._fernet().decrypt(value.encode()).decode())

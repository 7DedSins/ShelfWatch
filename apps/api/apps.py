from django.apps import AppConfig


class ApiConfig(AppConfig):
    """HTTP JSON API. Dotted name must match INSTALLED_APPS (`apps.api`)."""

    name = "apps.api"

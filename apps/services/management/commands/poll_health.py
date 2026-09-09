"""python manage.py poll_health — naive poller (no Celery).

Loads every Service row and calls poll_health. Connector failures print
on stderr; they must not look like "no services" / empty inventory.
"""

from django.core.management.base import BaseCommand

from apps.services.connectors.base import ConnectorError
from apps.services.health import poll_health
from apps.services.models import Service


class Command(BaseCommand):
    help = "Poll health for each Service row (Kavita, LANraragi, …)."

    def handle(self, *args, **options):
        services = Service.objects.all()
        if not services:
            self.stdout.write("No services.")
            return

        for service in services:
            try:
                result = poll_health(service)
                detail = f" {result.detail}" if result.detail else ""
                self.stdout.write(
                    self.style.SUCCESS(f"{service.name}: ok={result.ok}{detail}")
                )
            except ConnectorError as extra:
                self.stderr.write(
                    self.style.ERROR(f"{service.name}: {extra}")
                )

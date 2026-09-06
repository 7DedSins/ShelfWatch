from django.urls import resolve, reverse

from apps.core.views import healthz


def test_healthz_url_reverses_and_resolves():
    # Unnamed path: we resolve by path, not reverse() by name.
    match = resolve("/healthz/")
    assert match.func is healthz


def test_admin_url_still_resolves():
    assert reverse("admin:index") == "/admin/"

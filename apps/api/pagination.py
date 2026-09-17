"""Page-number lists. No cursor: there is no HealthCheck log table."""

from rest_framework.pagination import PageNumberPagination as DRFPageNumberPagination


class PageNumberPagination(DRFPageNumberPagination):
    """``?page=`` plus optional ``?page_size=`` (capped)."""

    page_size_query_param = "page_size"
    max_page_size = 100


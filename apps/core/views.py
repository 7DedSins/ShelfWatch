from django.db import connection
from django.http import JsonResponse


# Create your views here.
def healthz(request):
    try:
        connection.ensure_connection()
        return JsonResponse({"status": "ok"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "detail": str(e)}, status=503)

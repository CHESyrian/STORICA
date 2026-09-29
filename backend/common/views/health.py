"""
Lightweight health-check endpoint for the STORICA API.

Used by the desktop client for offline detection and by load balancers /
monitoring. Intentionally unauthenticated and free of heavy DB work.
"""
from django.db import connection
from django.http import JsonResponse
from django.views import View


class HealthCheckView(View):
    """
    GET /api/health/

    Returns 200 + JSON when the process is up and the database is reachable.
    Returns 503 when the database check fails.
    """

    def get(self, request, *args, **kwargs):
        db_ok = False
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_ok = cursor.fetchone() is not None
        except Exception:
            db_ok = False

        payload = {
            "status": "ok" if db_ok else "degraded",
            "service": "storica-api",
            "database": "up" if db_ok else "down",
        }
        status_code = 200 if db_ok else 503
        return JsonResponse(payload, status=status_code)

"""Liveness probe for load balancers and Docker (cheap process check)."""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET


@csrf_exempt
@require_GET
def liveness(request):
    return JsonResponse({"status": "alive"})

"""
Optional QA quick-login stub — copy/adapt when adding demo mode.

GET /api/v1/<your-app>/auth/qa-accounts/  → 404 when DEMO_ENABLED is off.

See CondHOA user/qa_accounts.py for a full implementation (domain-filtered catalog).
"""
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class QaAccountsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        if not getattr(settings, "DEMO_ENABLED", False):
            return Response(status=404)
        return Response({"groups": []})

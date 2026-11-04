from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest

_current_request: ContextVar[HttpRequest | None] = ContextVar("backstage_current_request", default=None)


def get_current_request() -> HttpRequest | None:
    return _current_request.get()


class AdminRequestMiddleware:
    """Stores the active request for admin audit metadata (IP on LogEntry sidecar)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = _current_request.set(request)
        try:
            return self.get_response(request)
        finally:
            _current_request.reset(token)

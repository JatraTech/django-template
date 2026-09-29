from __future__ import annotations

from typing import Any

from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.http import HttpRequest


class PreviewTokenService:
    SALT = "backstage-preview"
    MAX_AGE = 900

    def generate(self, user_id: int, obj: Any) -> str:
        signer = TimestampSigner(salt=self.SALT)
        value = f"{user_id}:{obj._meta.app_label}:{obj._meta.model_name}:{obj.pk}"
        return signer.sign(value)

    def validate(self, token: str) -> dict[str, Any] | None:
        signer = TimestampSigner(salt=self.SALT)
        try:
            value = signer.unsign(token, max_age=self.MAX_AGE)
        except (BadSignature, SignatureExpired):
            return None
        user_pk, app_label, model_name, obj_pk = value.split(":", 3)
        return {
            "user_pk": int(user_pk),
            "app_label": app_label,
            "model_name": model_name,
            "pk": int(obj_pk),
        }


def get_preview_from_request(request: HttpRequest) -> dict[str, Any] | None:
    token = request.headers.get("X-Preview-Token") or request.GET.get("preview")
    if not token:
        return None
    return PreviewTokenService().validate(token)

from __future__ import annotations

import ipaddress

from backstage.settings import get_config


def _valid(candidate: str) -> str | None:
    try:
        return str(ipaddress.ip_address((candidate or "").strip()))
    except ValueError:
        return None


def trusted_proxy_count() -> int | None:
    value = get_config().get("TRUSTED_PROXY_COUNT")
    if value is None:
        return None
    return int(value)


def client_ip_from(forwarded: str, remote_addr: str, num_proxies: int | None) -> str | None:
    entries = [part.strip() for part in (forwarded or "").split(",") if part.strip()]
    if num_proxies == 0 or not entries:
        candidate = remote_addr or ""
    elif num_proxies:
        candidate = entries[-min(int(num_proxies), len(entries))]
    else:
        candidate = entries[0]
    return _valid(candidate) or _valid(remote_addr or "")


def client_ip(request) -> str | None:
    if request is None:
        return None
    meta = getattr(request, "META", None) or {}
    return client_ip_from(
        meta.get("HTTP_X_FORWARDED_FOR", ""),
        meta.get("REMOTE_ADDR", ""),
        trusted_proxy_count(),
    )

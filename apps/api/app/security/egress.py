import os
from urllib.parse import urlparse

_allow = {
    h.strip().lower() for h in os.getenv("EGRESS_ALLOWLIST", "").split(",") if h.strip()
}


def is_allowed(hostname: str) -> bool:
    if not _allow:
        return False
    hn = hostname.lower()
    return any(hn == d or hn.endswith(f".{d}") for d in _allow)


def guard_outbound(url: str):
    host = urlparse(url).hostname or ""
    if not is_allowed(host):
        raise RuntimeError(f"Egress blocked to host: {host}")

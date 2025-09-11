import base64
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Callable

from fastapi import HTTPException
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from app.core.config import settings
from packages.schemas.license import License

# Embedded public key for license verification
PUBLIC_KEY_B64 = "5ZyKDtcNYw4keTd5Oq8IWN9sEx0sTy2scgihTK7tBqc="
VERIFY_KEY = VerifyKey(base64.b64decode(PUBLIC_KEY_B64))

_current_license: License | None = None


class LicenseError(Exception):
    """Raised when the license is missing or invalid."""


def load_license() -> None:
    """Load and verify the license from disk."""
    global _current_license
    path = Path(settings.LICENSE_FILE)
    if not path.exists():
        raise LicenseError("License file not found")
    data = json.loads(path.read_text())
    sig_b64 = data.get("sig")
    if not sig_b64:
        raise LicenseError("License missing signature")
    payload = data.copy()
    payload.pop("sig", None)
    payload_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    try:
        VERIFY_KEY.verify(payload_bytes, base64.b64decode(sig_b64))
    except BadSignatureError as exc:  # pragma: no cover - explicit
        raise LicenseError("Invalid license signature") from exc
    _current_license = License(**data)


def get_license() -> License | None:
    return _current_license


def ensure_not_expired() -> None:
    lic = get_license()
    if not lic:
        raise HTTPException(status_code=403, detail="License missing")
    expiry = lic.expiry + timedelta(days=14)
    if date.today() > expiry:
        raise HTTPException(status_code=403, detail="License expired")


def check_seats(active_users: int) -> None:
    lic = get_license()
    if lic and active_users > lic.seats:
        raise HTTPException(status_code=403, detail="Seat limit exceeded")


def license_required(feature: str) -> Callable[[], None]:
    def dependency() -> None:
        lic = get_license()
        if not lic:
            raise HTTPException(status_code=403, detail="License missing")
        ensure_not_expired()
        if lic.edition != "enterprise":
            raise HTTPException(status_code=402, detail="Enterprise edition required")
        if feature not in lic.features:
            raise HTTPException(status_code=402, detail="Feature not licensed")

    return dependency


__all__ = [
    "load_license",
    "get_license",
    "check_seats",
    "license_required",
    "LicenseError",
]

"""Settings endpoints requiring admin role."""

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..core.security import RoleChecker, get_current_user
from ..core.license import LicenseError, get_license, load_license
from ..core.config import settings
from ..services.audit import record

router = APIRouter(prefix="/settings", tags=["settings"])

admin_only = RoleChecker(["admin"])


@router.get("/", dependencies=[Depends(admin_only)])
async def read_settings() -> dict:
    """Protected settings endpoint."""
    return {"secret": True}


@router.get("/license", dependencies=[Depends(admin_only)])
def get_license_info() -> dict:
    lic = get_license()
    if not lic:
        return {"valid": False}
    return {
        "org": lic.org,
        "edition": lic.edition,
        "features": lic.features,
        "seats": lic.seats,
        "expiry": lic.expiry.isoformat(),
        "valid": True,
    }


@router.post("/license/upload", dependencies=[Depends(admin_only)])
async def upload_license(
    file: UploadFile = File(...), user: dict = Depends(get_current_user)
) -> dict:
    data = await file.read()
    Path(settings.LICENSE_FILE).write_bytes(data)
    try:
        load_license()
    except LicenseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    record("LICENSE_UPLOAD", actor=user.get("username"))
    return {"status": "ok"}


"""Settings endpoints requiring admin role."""

from fastapi import APIRouter, Depends

from ..core.security import RoleChecker

router = APIRouter(prefix="/settings", tags=["settings"])

admin_only = RoleChecker(["admin"])


@router.get("/", dependencies=[Depends(admin_only)])
async def read_settings() -> dict:
    """Protected settings endpoint."""
    return {"secret": True}


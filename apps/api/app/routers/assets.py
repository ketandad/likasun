"""Assets endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/")
async def list_assets() -> list:
    return []


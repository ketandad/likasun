"""Health check endpoint."""

from typing import Any

from fastapi import APIRouter

from app.__version__ import __version__

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def get_health() -> dict[str, Any]:
    """Return service health."""
    return {"ok": True, "version": __version__}


"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def get_health() -> dict[str, bool]:
    """Return service health."""
    return {"ok": True}


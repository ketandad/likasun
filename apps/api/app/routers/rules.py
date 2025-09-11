"""Rules endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/rules", tags=["rules"])


@router.get("/")
async def list_rules() -> list:
    return []


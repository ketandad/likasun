"""Documents endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/")
async def list_documents() -> list:
    return []


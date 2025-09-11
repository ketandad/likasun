"""Compliance endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.get("/")
async def list_compliance() -> list:
    return []


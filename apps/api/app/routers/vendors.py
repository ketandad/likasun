"""Vendors endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/vendors", tags=["vendors"])


@router.get("/")
async def list_vendors() -> list:
    return []


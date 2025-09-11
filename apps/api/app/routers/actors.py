"""Actors endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/actors", tags=["actors"])


@router.get("/")
async def list_actors() -> list:
    return []


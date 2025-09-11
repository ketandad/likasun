"""Evaluate endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/evaluate", tags=["evaluate"])


@router.get("/")
async def evaluate_stub() -> dict:
    return {"result": "pending"}


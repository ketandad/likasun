"""Exception management endpoints."""

from __future__ import annotations

from datetime import date
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import RoleChecker, get_current_user
from app.dependencies import get_db
from app.models import controls as control_m
from app.models import exceptions as exc_m

router = APIRouter(prefix="/exceptions", tags=["exceptions"])

admin_only = RoleChecker(["admin"])


class ExceptionCreate(BaseModel):
    control_id: str
    selector: dict
    reason: str
    expires_at: date = Field(..., description="Expiration date")


class ExceptionOut(BaseModel):
    id: UUID
    control_id: str
    selector: dict
    reason: str
    expires_at: date
    created_by: str
    created_at: datetime

    class Config:
        orm_mode = True


@router.post("/", dependencies=[Depends(admin_only)], response_model=ExceptionOut)
def create_exception(
    data: ExceptionCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> ExceptionOut:
    today = date.today()
    if data.expires_at < today:
        raise HTTPException(status_code=400, detail="expires_at must be today or later")
    if not set(data.selector).intersection({"asset_id", "type", "env", "cloud"}):
        raise HTTPException(status_code=400, detail="selector must include asset_id, type, env or cloud")
    exists_control = (
        db.query(control_m.Control)
        .filter(control_m.Control.control_id == data.control_id)
        .first()
    )
    if not exists_control:
        raise HTTPException(status_code=400, detail="control_id does not exist")
    dup = (
        db.query(exc_m.Exception)
        .filter(
            exc_m.Exception.control_id == data.control_id,
            exc_m.Exception.selector == data.selector,
            exc_m.Exception.expires_at >= today,
        )
        .first()
    )
    if dup:
        raise HTTPException(status_code=400, detail="Duplicate active exception")
    exc = exc_m.Exception(
        control_id=data.control_id,
        selector=data.selector,
        reason=data.reason,
        expires_at=data.expires_at,
        created_by=user.get("username") or user.get("email", ""),
    )
    db.add(exc)
    db.commit()
    db.refresh(exc)
    return ExceptionOut.from_orm(exc)


@router.get("/", dependencies=[Depends(admin_only)], response_model=List[ExceptionOut])
def list_exceptions(
    active: bool | None = Query(None, description="Filter active exceptions"),
    db: Session = Depends(get_db),
) -> List[ExceptionOut]:
    query = db.query(exc_m.Exception)
    if active:
        today = date.today()
        query = query.filter(exc_m.Exception.expires_at >= today)
    excs = query.all()
    return [ExceptionOut.from_orm(e) for e in excs]


@router.delete("/{exc_id}", dependencies=[Depends(admin_only)])
def delete_exception(exc_id: UUID, db: Session = Depends(get_db)) -> dict:
    exc = db.get(exc_m.Exception, exc_id)
    if not exc:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(exc)
    db.commit()
    return {"deleted": True}

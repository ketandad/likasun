from __future__ import annotations

"""Audit logging helper."""

from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import db as models_db
from app.models.audit import AuditLog


def record(action: str, actor: str | None = None, resource: str | None = None, details: Any | None = None) -> None:
    try:
        session: Session = models_db.SessionLocal()
    except SQLAlchemyError:  # pragma: no cover - best effort when DB unavailable
        return
    try:
        log = AuditLog(actor=actor, action=action, resource=resource, details=details or {})
        session.add(log)
        session.commit()
    except SQLAlchemyError:  # pragma: no cover - ignore logging errors
        session.rollback()
    finally:
        session.close()


__all__ = ["record"]

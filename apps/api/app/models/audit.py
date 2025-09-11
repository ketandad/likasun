from __future__ import annotations

from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.sql import func

from .db import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = sa.Column(sa.String(), primary_key=True, default=lambda: str(uuid4()))
    ts = sa.Column(sa.DateTime(timezone=True), server_default=func.now(), nullable=False)
    actor = sa.Column(sa.String(), nullable=True)
    action = sa.Column(sa.String(), nullable=False)
    resource = sa.Column(sa.String(), nullable=True)
    details = sa.Column(sa.JSON(), nullable=False, server_default=sa.text("'{}'"))

    __table_args__ = (
        sa.Index("ix_audit_logs_ts_desc", "ts"),
        sa.Index("ix_audit_logs_action", "action"),
    )


__all__ = ["AuditLog"]

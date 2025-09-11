from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4
import uuid

from sqlalchemy import Date, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


from .db import Base


class Exception(Base):
    __tablename__ = "exceptions"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    control_id: Mapped[str] = mapped_column(
        String, ForeignKey("controls.control_id", ondelete="CASCADE")
    )
    # JSONB on Postgres, plain JSON elsewhere
    selector: Mapped[dict] = mapped_column(JSON, default=dict)
    reason: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[date] = mapped_column(Date)
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

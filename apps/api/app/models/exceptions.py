from datetime import datetime
from sqlalchemy import JSON, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Exception(Base):
    __tablename__ = "exceptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    control_id: Mapped[str] = mapped_column(String)
    selector: Mapped[dict] = mapped_column(JSON, default=dict)
    reason: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[str] = mapped_column(String)

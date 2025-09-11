from datetime import datetime
from sqlalchemy import JSON, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Actor(Base):
    __tablename__ = "actors"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    source: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    mfa: Mapped[bool] = mapped_column(Boolean)
    roles: Mapped[dict] = mapped_column(JSON, default=dict)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

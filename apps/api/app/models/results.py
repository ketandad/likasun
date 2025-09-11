from datetime import datetime
from sqlalchemy import JSON, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .db import Base


class Result(Base):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(primary_key=True)
    control_id: Mapped[str] = mapped_column(String)
    control_title: Mapped[str] = mapped_column(String)
    asset_id: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String)
    frameworks: Mapped[dict] = mapped_column(JSON, default=dict)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    fix: Mapped[dict] = mapped_column(JSON, default=dict)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    run_id: Mapped[str] = mapped_column(String, index=True)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

from datetime import datetime
from sqlalchemy import JSON, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .db import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[str] = mapped_column(String, index=True)
    cloud: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    region: Mapped[str] = mapped_column(String)
    tags: Mapped[dict] = mapped_column(JSON, default=dict)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    ingest_source: Mapped[str] = mapped_column(String)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

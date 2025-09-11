from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Control(Base):
    __tablename__ = "controls"

    id: Mapped[int] = mapped_column(primary_key=True)
    control_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String)
    applies_to: Mapped[dict] = mapped_column(JSON, default=dict)
    logic: Mapped[dict] = mapped_column(JSON, default=dict)
    frameworks: Mapped[dict] = mapped_column(JSON, default=dict)
    fix: Mapped[dict] = mapped_column(JSON, default=dict)

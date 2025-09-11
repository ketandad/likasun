from datetime import date
from sqlalchemy import JSON, String, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    doc_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    kind: Mapped[str] = mapped_column(String)
    parties: Mapped[dict] = mapped_column(JSON, default=dict)
    renewal_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    obligations: Mapped[dict] = mapped_column(JSON, default=dict)
    clauses: Mapped[dict] = mapped_column(JSON, default=dict)
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

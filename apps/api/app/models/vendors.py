from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(primary_key=True)
    vendor_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    product: Mapped[str] = mapped_column(String)
    scopes: Mapped[dict] = mapped_column(JSON, default=dict)
    data_classes: Mapped[dict] = mapped_column(JSON, default=dict)
    dpia_status: Mapped[str] = mapped_column(String)
    risk: Mapped[str] = mapped_column(String)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

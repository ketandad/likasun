from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Meta(Base):
    __tablename__ = "meta"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(Text)

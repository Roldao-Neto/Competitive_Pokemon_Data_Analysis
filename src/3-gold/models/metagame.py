from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Metagame(Base):
    __tablename__ = "metagame"

    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("smogon_category.id"), primary_key=True
    )
    rating: Mapped[int] = mapped_column(Integer, primary_key=True)
    n_battles: Mapped[int] = mapped_column(Integer)

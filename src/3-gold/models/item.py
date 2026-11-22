from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Item(Base):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(Text)
    fling_power: Mapped[int | None] = mapped_column(Integer)
    fling_effect: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("item_category.id"))
    effect: Mapped[str | None] = mapped_column(Text)
    short_effect: Mapped[str | None] = mapped_column(Text)

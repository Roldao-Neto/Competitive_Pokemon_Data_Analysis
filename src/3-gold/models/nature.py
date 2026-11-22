from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Nature(Base):
    __tablename__ = "nature"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(Text)
    decreased_stat_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("stat.id")
    )
    increased_stat_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("stat.id")
    )
    likes_flavor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("flavor.id")
    )
    hates_flavor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("flavor.id")
    )

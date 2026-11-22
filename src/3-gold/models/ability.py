from sqlalchemy import Integer, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Ability(Base):
    __tablename__ = "ability"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(Text)
    effect: Mapped[str] = mapped_column(Text)
    short_effect: Mapped[str] = mapped_column(Text)
    generation: Mapped[int] = mapped_column(SmallInteger)

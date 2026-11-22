from sqlalchemy import ForeignKey, Integer, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Move(Base):
    __tablename__ = "move"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(Text)
    accuracy: Mapped[int | None] = mapped_column(SmallInteger)
    effect_chance: Mapped[int | None] = mapped_column(SmallInteger)
    pp: Mapped[int] = mapped_column(SmallInteger)
    priority: Mapped[int] = mapped_column(SmallInteger)
    power: Mapped[int | None] = mapped_column(Integer)
    damage_class_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("damage_class.id")
    )
    target_id: Mapped[int] = mapped_column(Integer, ForeignKey("target.id"))
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey("type.id"))
    generation: Mapped[int] = mapped_column(SmallInteger)
    min_hits: Mapped[int | None] = mapped_column(SmallInteger)
    max_hits: Mapped[int | None] = mapped_column(SmallInteger)
    min_turns: Mapped[int | None] = mapped_column(SmallInteger)
    max_turns: Mapped[int | None] = mapped_column(SmallInteger)
    drain: Mapped[int | None] = mapped_column(SmallInteger)
    healing: Mapped[int | None] = mapped_column(SmallInteger)
    crit_rate: Mapped[int | None] = mapped_column(SmallInteger)
    ailment_chance: Mapped[int | None] = mapped_column(SmallInteger)
    flinch_chance: Mapped[int | None] = mapped_column(SmallInteger)
    stat_chance: Mapped[int | None] = mapped_column(SmallInteger)
    ailment_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("ailment.id"))
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("move_category.id")
    )
    effect: Mapped[str | None] = mapped_column(Text)
    short_effect: Mapped[str | None] = mapped_column(Text)


class MoveStatChange(Base):
    __tablename__ = "move_stat_change"

    move_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("move.id"), primary_key=True
    )
    stat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stat.id"), primary_key=True
    )
    change: Mapped[int] = mapped_column(SmallInteger)

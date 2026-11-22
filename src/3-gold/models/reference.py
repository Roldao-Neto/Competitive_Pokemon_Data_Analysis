from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Type(Base):
    __tablename__ = "type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(Text)
    generation: Mapped[int] = mapped_column(SmallInteger)


class Stat(Base):
    __tablename__ = "stat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text)


class MoveCategory(Base):
    __tablename__ = "move_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text)


class Target(Base):
    __tablename__ = "target"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text)


class Ailment(Base):
    __tablename__ = "ailment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text)


class DamageClass(Base):
    __tablename__ = "damage_class"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text)


class SmogonCategory(Base):
    __tablename__ = "smogon_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    tier_order: Mapped[int] = mapped_column(SmallInteger)


class ItemCategory(Base):
    __tablename__ = "item_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text)


class Flavor(Base):
    __tablename__ = "flavor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text)


class Species(Base):
    __tablename__ = "species"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    is_legendary: Mapped[bool] = mapped_column(Boolean)
    is_mythical: Mapped[bool] = mapped_column(Boolean)
    generation: Mapped[int] = mapped_column(SmallInteger)


class TypeEffect(Base):
    __tablename__ = "type_effect"

    attacking_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("type.id"), primary_key=True
    )
    defending_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("type.id"), primary_key=True
    )
    multiplier: Mapped[Decimal] = mapped_column(Numeric(2, 1))

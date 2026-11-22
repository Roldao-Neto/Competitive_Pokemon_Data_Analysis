from datetime import datetime

from sqlalchemy import (
    DateTime,
    Double,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    SmallInteger,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Usage(Base):
    __tablename__ = "usage"
    __table_args__ = (
        ForeignKeyConstraint(
            ["date", "category_id", "rating"],
            ["metagame.date", "metagame.category_id", "metagame.rating"],
            name="fk_usage_metagame",
        ),
        UniqueConstraint(
            "date",
            "category_id",
            "rating",
            "pokemon_id",
            name="uq_usage_date_category_rating_pokemon",
        ),
    )

    usage_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    category_id: Mapped[int] = mapped_column(Integer)
    rating: Mapped[int] = mapped_column(Integer)
    pokemon_id: Mapped[int] = mapped_column(Integer, ForeignKey("pokemon.id"))
    raw_count: Mapped[int] = mapped_column(Integer)
    usage: Mapped[float] = mapped_column(Double)
    viability_players: Mapped[int] = mapped_column(Integer)
    viability_top_gxe: Mapped[int] = mapped_column(SmallInteger)
    viability_99th_gxe: Mapped[int] = mapped_column(SmallInteger)
    viability_95th_gxe: Mapped[int] = mapped_column(SmallInteger)


class UsageAbility(Base):
    __tablename__ = "usage_ability"

    usage_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usage.usage_id"), primary_key=True
    )
    ability_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ability.id"), primary_key=True
    )
    weight: Mapped[float] = mapped_column(Double)


class UsageItem(Base):
    __tablename__ = "usage_item"

    usage_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usage.usage_id"), primary_key=True
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("item.id"), primary_key=True
    )
    weight: Mapped[float] = mapped_column(Double)


class UsageMove(Base):
    __tablename__ = "usage_move"

    usage_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usage.usage_id"), primary_key=True
    )
    move_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("move.id"), primary_key=True
    )
    weight: Mapped[float] = mapped_column(Double)


class UsageSpread(Base):
    __tablename__ = "usage_spread"

    usage_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usage.usage_id"), primary_key=True
    )
    nature_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("nature.id"), primary_key=True
    )
    hp_ev: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    attack_ev: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    defense_ev: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    special_attack_ev: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    special_defense_ev: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    speed_ev: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    weight: Mapped[float] = mapped_column(Double)


class UsageTeraType(Base):
    __tablename__ = "usage_tera_type"

    usage_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usage.usage_id"), primary_key=True
    )
    type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("type.id"), primary_key=True
    )
    weight: Mapped[float] = mapped_column(Double)


class UsageTeammate(Base):
    __tablename__ = "usage_teammate"

    usage_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usage.usage_id"), primary_key=True
    )
    teammate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pokemon.id"), primary_key=True
    )
    weight: Mapped[float] = mapped_column(Double)


class UsageCheckCounter(Base):
    __tablename__ = "usage_check_counter"

    usage_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usage.usage_id"), primary_key=True
    )
    counter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pokemon.id"), primary_key=True
    )
    n: Mapped[float] = mapped_column(Double)
    p: Mapped[float] = mapped_column(Double)
    d: Mapped[float] = mapped_column(Double)

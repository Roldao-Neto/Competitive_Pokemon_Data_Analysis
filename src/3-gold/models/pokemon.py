from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Pokemon(Base):
    __tablename__ = "pokemon"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, unique=True)
    weight: Mapped[int | None] = mapped_column(Integer)
    species_id: Mapped[int] = mapped_column(Integer, ForeignKey("species.id"))
    hp: Mapped[int] = mapped_column(Integer)
    attack: Mapped[int] = mapped_column(Integer)
    defense: Mapped[int] = mapped_column(Integer)
    special_attack: Mapped[int] = mapped_column(Integer)
    special_defense: Mapped[int] = mapped_column(Integer)
    speed: Mapped[int] = mapped_column(Integer)
    type_1_id: Mapped[int] = mapped_column(Integer, ForeignKey("type.id"))
    type_2_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("type.id"))
    ability_1_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("ability.id"))
    ability_2_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("ability.id"))
    hidden_ability_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("ability.id"))
    is_fully_evolved: Mapped[bool] = mapped_column(Boolean)


class PokemonMove(Base):
    __tablename__ = "pokemon_moves"

    pokemon_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pokemon.id"), primary_key=True
    )
    move_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("move.id"), primary_key=True
    )

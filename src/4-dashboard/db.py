import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

# Same default as the gold notebook; every connection is read-only, so the dashboard can never change the database
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://pokemon:pokemon@127.0.0.1:5432/pokemon")


@st.cache_resource
def get_engine():
    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"options": "-c default_transaction_read_only=on"},
    )


@st.cache_data(show_spinner=False)
def query(sql: str, **params) -> pd.DataFrame:
    with get_engine().connect() as connection:
        return pd.read_sql(text(sql), connection, params=params)


# Every (tier, month, rating) that has usage rows
def metagames() -> pd.DataFrame:
    return query("""
        SELECT sc.id AS category_id, sc.code, sc.name AS tier, sc.tier_order, m.date, m.rating, m.n_battles
        FROM metagame m
        JOIN smogon_category sc ON sc.id = m.category_id
        WHERE EXISTS (SELECT 1 FROM usage u WHERE (u.date, u.category_id, u.rating) = (m.date, m.category_id, m.rating))
        ORDER BY sc.tier_order, m.date, m.rating
    """)


# The tier / month / rating chosen in the sidebar (set by app.py before every page runs)
def selected() -> dict:
    return st.session_state["metagame"]


# The selection as query parameters
def params() -> dict:
    metagame = selected()
    return {"category_id": metagame["category_id"], "date": metagame["date"], "rating": metagame["rating"]}


# "OU · 2026-08 · rating ≥ 1500", shown under each page title
def describe(month: bool = True) -> str:
    metagame = selected()
    parts = [metagame["tier"]]

    if month:
        parts.append(f"{metagame['date']:%Y-%m}")

    parts.append("todos os jogadores" if metagame["rating"] == 0 else f"rating ≥ {metagame['rating']}")
    return " · ".join(parts)

import streamlit as st

from charts import number
from db import metagames

st.set_page_config(page_title="Meta Competitivo Gen 9", page_icon="📊")

# Shared filters: chosen once here, read by every page through db.selected()
options = metagames()

with st.sidebar:
    st.title("Meta Gen 9")

    tiers = options.drop_duplicates("code")
    tier = st.selectbox(
        "Tier",
        tiers["code"],
        index=int((tiers["code"] == "ou").to_numpy().argmax()),
        format_func=dict(zip(tiers["code"], tiers["tier"])).get,
    )
    tier_options = options[options["code"] == tier]

    months = tier_options["date"].drop_duplicates().sort_values(ascending=False)
    month = st.selectbox("Mês", months, format_func=lambda date: f"{date:%Y-%m}")
    month_options = tier_options[tier_options["date"] == month]

    ratings = month_options["rating"].to_list()
    rating = st.selectbox("Corte de rating", ratings, index=ratings.index(1500) if 1500 in ratings else 0,
                          format_func=lambda value: "0 (todos os jogadores)" if value == 0 else f"{value}+")

    current = month_options[month_options["rating"] == rating].iloc[0]
    st.caption(f"{number(current['n_battles'])} batalhas em {current['tier']} neste mês")

st.session_state["metagame"] = {
    "category_id": int(current["category_id"]),
    "code": tier,
    "tier": current["tier"],
    "date": month.to_pydatetime(),
    "rating": int(rating),
}


pages = [
    st.Page("views/questions.py", title="Perguntas norteadoras", icon=":material/help:", default=True),
    st.Page("views/usage.py", title="Uso", icon=":material/leaderboard:"),
    st.Page("views/trends.py", title="Tendências e tiers", icon=":material/trending_up:"),
    st.Page("views/skill_gap.py", title="Diferença de habilidade", icon=":material/military_tech:"),
    st.Page("views/sets.py", title="Sets", icon=":material/inventory_2:"),
    st.Page("views/pokemon.py", title="Pokémon", icon=":material/pets:"),
    st.Page("views/cores.py", title="Cores e matchups", icon=":material/group:"),
    st.Page("views/meta.py", title="Composição do meta", icon=":material/category:"),
]

st.navigation(pages).run()

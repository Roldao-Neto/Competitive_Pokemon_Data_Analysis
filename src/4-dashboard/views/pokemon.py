import altair as alt
import streamlit as st

from charts import bars, lines, number, view
from db import describe, params, selected
from queries import counters, metagame_usage, pokemon_entries, tier_history

metagame = selected()
usage = metagame_usage(**params())

st.title("Pokémon")
st.caption(describe())

# Keep the chosen Pokémon when the filters change, as long as it is used in the new metagame
names = usage["name"].to_list()
previous = st.session_state.get("pokemon")
name = st.selectbox("Pokémon", names, index=names.index(previous) if previous in names else 0)
st.session_state["pokemon"] = name

row = usage[usage["name"] == name].iloc[0]

left, middle, right = st.columns(3)
left.metric("Uso", f"{row['usage_pct']:.2f}%")
middle.metric("Posição", f"#{row['rank']} de {len(usage)}")
right.metric("GXE do melhor jogador", f"{row['viability_top_gxe']}", help=f"{number(row['viability_players'])} jogadores o usam")

section = view({
    "tendencia": "Tendência",
    "habilidades": "Habilidades",
    "itens": "Itens",
    "golpes": "Golpes",
    "tera": "Tera types",
    "spreads": "Spreads",
    "companheiros": "Companheiros",
    "counters": "Counters",
}, key="pokemon_view")

if section == "tendencia":
    history = tier_history(metagame["category_id"], metagame["rating"])
    lines(history[history["name"] == name], "usage_pct", "name", "Uso (% dos times)")

elif section == "counters":
    answers = counters(int(row["usage_id"])).head(10)
    bars(answers, "score", "name", "Pontuação de counter", tooltip=[
        alt.Tooltip("ko_or_switch_pct:Q", title=f"{name} nocauteado ou forçado a trocar (%)", format=".1f"),
        alt.Tooltip("std_pct:Q", title="Desvio padrão (%)", format=".1f"),
        alt.Tooltip("n:Q", title="Confrontos", format=",.0f"),
    ])
    st.caption(f"Checks e counters do Smogon: pontuação = chance de o confronto terminar com {name} nocauteado ou forçado "
               "a trocar, menos 4 desvios padrão. Apenas confrontos vistos pelo menos 20 vezes.")

else:
    over_time = st.toggle("Mostrar como mudou ao longo do tempo", key="pokemon_over_time")

    if not over_time:
        entries = pokemon_entries(section, int(row["pokemon_id"]), **params()).head(10)
        bars(entries, "pct", "name", f"% dos sets de {name}" if section != "companheiros" else f"% dos times de {name}")
    else:
        history = pokemon_entries(section, int(row["pokemon_id"]), metagame["category_id"], metagame["rating"])
        top = history[history["date"] == history["date"].max()].nlargest(5, "pct")["name"]
        lines(history[history["name"].isin(top)], "pct", "name", "% dos sets")
        st.caption("As 5 entradas mais comuns do último mês em que este Pokémon foi usado, ao longo dos meses.")

    if section == "golpes":
        st.caption("Cada set tem 4 golpes, então as porcentagens de golpes somam cerca de 400%.")

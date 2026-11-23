import altair as alt
import pandas as pd
import streamlit as st

from charts import dots, view
from db import describe, metagames, params, selected
from queries import metagame_usage

metagame = selected()
usage = metagame_usage(**params())
everyone = metagame_usage(metagame["category_id"], metagame["date"], 0)

st.title("Diferença de habilidade")
st.caption(describe())

# Pokémon filter for the whole page: empty = each view picks the Pokémon to show by itself.
# Options: every Pokémon of the month (rating 0 has them all), the ones used at the chosen cutoff first
options = pd.concat([usage["name"], everyone["name"]]).drop_duplicates().to_list()
previous = [name for name in st.session_state.get("skill_pokemon", []) if name in options]
chosen = st.multiselect("Pokémon", options, default=previous, placeholder="Todos (escolha para filtrar)",
                        help="Sem seleção, cada visão escolhe sozinha os Pokémon em destaque")
st.session_state["skill_pokemon"] = chosen


def not_used(names) -> None:
    """Chosen Pokémon that the current rating cutoff does not have."""
    if missing := [name for name in chosen if name not in set(names)]:
        st.info(f"Sem dados neste corte de rating: {', '.join(missing)}")


choice = view({
    "todos_vs_topo": "Todos vs topo do ladder",
    "teto": "Teto de viabilidade",
    "gxe": "Distribuição de GXE",
}, key="skill_view")

if choice == "todos_vs_topo":
    available = metagames()
    available = available[(available["code"] == metagame["code"]) & (available["date"] == metagame["date"])]
    top_rating = int(available["rating"].max())

    top = metagame_usage(metagame["category_id"], metagame["date"], top_rating)[["name", "usage_pct"]]

    # A Pokémon missing at the top cutoff is simply not used there: 0%
    both = everyone[["name", "usage_pct"]].merge(top, on="name", how="outer", suffixes=("_everyone", "_top")).fillna(0)
    both["gap"] = both["usage_pct_top"] - both["usage_pct_everyone"]
    relevant = both[both[["usage_pct_everyone", "usage_pct_top"]].max(axis=1) >= 1]

    left, right = st.columns(2)
    favourite, dropped = relevant.loc[relevant["gap"].idxmax()], relevant.loc[relevant["gap"].idxmin()]
    left.metric("Mais favorecido no topo", favourite["name"], f"{favourite['gap']:+.1f} pts")
    right.metric("Mais deixado de lado no topo", dropped["name"], f"{dropped['gap']:+.1f} pts")

    if chosen:
        gaps = both[both["name"].isin(chosen)]
        caption = "Os Pokémon escolhidos no filtro."
    else:
        gaps = relevant.reindex(relevant["gap"].abs().sort_values(ascending=False).index).head(20)
        caption = ("Os 20 Pokémon cujo uso mais difere entre todos os jogadores e o maior corte de rating "
                   "(Pokémon acima de 1% de uso em pelo menos um dos dois).")

    long = gaps.melt(id_vars=["name", "gap"], value_vars=["usage_pct_everyone", "usage_pct_top"], var_name="ladder", value_name="usage")
    long["ladder"] = long["ladder"].map({"usage_pct_everyone": "Todos (0)", "usage_pct_top": f"Topo do ladder ({top_rating}+)"})
    order = gaps.sort_values("gap", ascending=False)["name"].to_list()

    base = alt.Chart(long).encode(y=alt.Y("name:N", sort=order, title=None))
    rule = base.mark_rule(color="#bbbbbb").encode(x="min(usage):Q", x2="max(usage):Q")
    points = base.mark_circle(size=90).encode(
        x=alt.X("usage:Q", title="Uso (% dos times)"),
        color=alt.Color("ladder:N", title=None, legend=alt.Legend(orient="bottom")),
        tooltip=[alt.Tooltip("name:N", title=" "), alt.Tooltip("ladder:N", title="Ladder"),
                 alt.Tooltip("usage:Q", title="Uso (%)", format=".1f"), alt.Tooltip("gap:Q", title="Diferença (pts)", format="+.1f")],
    )
    st.altair_chart((rule + points).properties(height=max(160, 26 * len(gaps))), width="stretch")
    st.caption(caption)

elif choice == "teto":
    tooltip = [alt.Tooltip("viability_99th_gxe:Q", title="GXE do percentil 99"), alt.Tooltip("viability_95th_gxe:Q", title="GXE do percentil 95"),
               alt.Tooltip("viability_players:Q", title="Jogadores", format=","), alt.Tooltip("usage_pct:Q", title="Uso (%)", format=".1f")]

    if chosen:
        not_used(usage["name"])
        shown = usage[usage["name"].isin(chosen)]
        note = "Os Pokémon escolhidos no filtro (o mínimo de jogadores não se aplica a eles)."
    else:
        min_players = st.slider("Mínimo de jogadores que o usam", 1, 500, 50, key="skill_players",
                                help="A viabilidade é medida nos jogadores que usam o Pokémon, então poucos jogadores a deixam ruidosa")
        shown = usage[usage["viability_players"] >= min_players].nlargest(15, ["viability_top_gxe", "viability_99th_gxe"])
        note = "Os 15 Pokémon com o maior teto."

    dots(shown, "viability_top_gxe", "name", "GXE do melhor jogador", tooltip=tooltip)
    st.caption(f"{note} Teto de viabilidade: o GXE (chance esperada de vencer um jogador aleatório) dos melhores jogadores "
               "que usam cada Pokémon. Ele mede os jogadores, não o Pokémon.")

else:
    min_players = st.slider("Mínimo de jogadores que o usam", 1, 500, 50, key="skill_players",
                            help="A viabilidade é medida nos jogadores que usam o Pokémon, então poucos jogadores a deixam ruidosa")
    trusted = usage[usage["viability_players"] >= min_players]

    histogram = alt.Chart(trusted).mark_bar(color="#9db4c0").encode(
        x=alt.X("viability_top_gxe:Q", bin=alt.Bin(step=2), title="GXE do melhor jogador"),
        y=alt.Y("count():Q", title="Pokémon"),
        tooltip=[alt.Tooltip("count():Q", title="Pokémon")],
    )
    chart = histogram

    # Chosen Pokémon: a line at their GXE, to see where they fall in the tier
    if chosen:
        not_used(usage["name"])
        marked = usage[usage["name"].isin(chosen)]
        marks = alt.Chart(marked).encode(
            x="viability_top_gxe:Q",
            tooltip=[alt.Tooltip("name:N", title=" "), alt.Tooltip("viability_top_gxe:Q", title="GXE do melhor jogador"),
                     alt.Tooltip("viability_players:Q", title="Jogadores", format=",")],
        )
        chart = histogram + marks.mark_rule(color="#e76f51", strokeWidth=2) + marks.mark_text(
            align="left", dx=4, y=8, color="#e76f51").encode(text="name:N")

    st.altair_chart(chart, width="stretch")
    st.caption(f"{len(trusted)} Pokémon usados por pelo menos {min_players} jogadores."
               + (" Linhas: os Pokémon escolhidos no filtro." if chosen else ""))

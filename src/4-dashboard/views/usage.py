import altair as alt
import streamlit as st

from charts import bars, number, view
from db import describe, params
from queries import metagame_usage

st.title("Uso")
st.caption(describe())

usage = metagame_usage(**params())
total = usage["usage_pct"].sum()
half = int((usage["usage_pct"].cumsum() < total / 2).sum()) + 1

left, middle, right = st.columns(3)
left.metric("Pokémon usados", number(len(usage)))
middle.metric("Mais usado", usage.iloc[0]["name"], help=f"{usage.iloc[0]['usage_pct']:.1f}% dos times")
right.metric("Metade de todo o uso", f"{half} Pokémon", help="Quantos dos Pokémon mais usados somam 50% de todas as escolhas")

choice = view({"mais_usados": "Pokémon mais usados", "concentracao": "Concentração do uso"}, key="usage_view")

if choice == "mais_usados":
    n = st.slider("Quantos", 5, 50, 15, key="usage_n")
    bars(usage.head(n), "usage_pct", "name", "Uso (% dos times)", tooltip=[alt.Tooltip("raw_count:Q", title="Contagem bruta", format=",")])
else:
    curve = usage.assign(cumulative=100 * usage["usage_pct"].cumsum() / total)
    line = alt.Chart(curve).mark_line().encode(
        x=alt.X("rank:Q", title="Pokémon, do mais ao menos usado"),
        y=alt.Y("cumulative:Q", title="Parcela de todas as escolhas (%)"),
        tooltip=[alt.Tooltip("rank:Q", title="Top"), alt.Tooltip("name:N", title="Até"), alt.Tooltip("cumulative:Q", title="Parcela (%)", format=".1f")],
    )
    rule = alt.Chart(curve.head(1)).mark_rule(strokeDash=[4, 4]).encode(y=alt.datum(50))
    st.altair_chart(line + rule, width="stretch")
    st.caption(f"Os {half} Pokémon mais usados somam metade de todas as escolhas deste metagame.")

st.caption("As estatísticas do Smogon são agregados mensais: mostram o que é usado, não o que vence. "
           "Não há taxas de vitória, times completos nem dados por batalha.")

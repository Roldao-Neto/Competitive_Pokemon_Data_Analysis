import altair as alt
import pandas as pd
import streamlit as st

from charts import bars, lines, view
from db import describe, metagames, selected
from queries import tier_history

metagame = selected()

st.title("Tendências e tiers")
st.caption(describe(month=False))

history = tier_history(metagame["category_id"], metagame["rating"])
months = sorted(history["date"].drop_duplicates())
current = pd.Timestamp(metagame["date"])


def month_label(date) -> str:
    return f"{date:%Y-%m}"


choice = view({
    "ao_longo_do_tempo": "Pokémon ao longo do tempo",
    "altas_quedas": "Altas e quedas",
    "novatos": "Novatos",
    "batalhas": "Batalhas por tier",
}, key="trends_view")

if choice == "ao_longo_do_tempo":
    top = history[history["date"] == current].nlargest(5, "usage_pct")["name"].to_list()
    chosen = st.multiselect("Pokémon", sorted(history["name"].unique()), default=top, key="trends_pokemon")
    lines(history[history["name"].isin(chosen)], "usage_pct", "name", "Uso (% dos times)")

elif choice == "altas_quedas":
    left, right = st.columns(2)
    start = left.selectbox("De", months, index=0, format_func=month_label, key="trends_from")
    end = right.selectbox("Até", months, index=months.index(current) if current in months else len(months) - 1,
                          format_func=month_label, key="trends_to")

    wide = history.pivot_table(index="name", columns="date", values="usage_pct").fillna(0)
    change = (wide[end] - wide[start]).rename("change").reset_index()
    movers = pd.concat([change.nlargest(10, "change"), change.nsmallest(10, "change")]).drop_duplicates("name")
    movers = movers[movers["change"] != 0]

    bars(movers, "change", "name", "Variação do uso (pontos percentuais)", fmt="+.1f",
         color=alt.condition(alt.datum.change > 0, alt.value("#2a9d8f"), alt.value("#e76f51")))

elif choice == "novatos":
    first_seen = history.groupby("name")["date"].min()
    newcomers = first_seen[first_seen > months[0]].rename("first_seen").reset_index()
    newcomers = newcomers.merge(history[history["date"] == current][["name", "usage_pct"]], on="name")
    newcomers = newcomers.sort_values("usage_pct", ascending=False)

    st.caption(f"Pokémon ausentes das estatísticas de {month_label(months[0])} deste tier e rating, ainda usados em {month_label(current)}.")
    st.dataframe(
        newcomers.assign(first_seen=newcomers["first_seen"].map(month_label)),
        hide_index=True,
        column_config={
            "name": "Pokémon",
            "first_seen": "Primeiro mês",
            "usage_pct": st.column_config.NumberColumn(f"Uso em {month_label(current)} (%)", format="%.2f"),
        },
    )

else:
    battles = metagames().drop_duplicates(["code", "date"])
    lines(battles.rename(columns={"tier": "Tier"}), "n_battles", "Tier", "Batalhas por mês", fmt=",")

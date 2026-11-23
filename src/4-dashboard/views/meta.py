import altair as alt
import streamlit as st

from charts import bars, from_link
from db import describe, params, query
from queries import METAGAME_TOTALS

st.title("Composição do meta")
st.caption(describe())


def types() -> None:
    share = query(METAGAME_TOTALS + """
        SELECT t.name, 100 * sum(u.usage) / (SELECT sum(usage) FROM u) AS share
        FROM u
        JOIN pokemon p ON p.id = u.pokemon_id
        JOIN "type" t ON t.id IN (p.type_1_id, p.type_2_id)
        GROUP BY t.name
        ORDER BY share DESC
    """, **params())

    bars(share, "share", "name", "% dos Pokémon usados com este tipo")
    st.caption("Tipos duplos contam para os dois tipos, então as parcelas somam mais de 100%. Os Tera types estão na página Sets.")


def coverage() -> None:
    hits = query(METAGAME_TOTALS + """
        , matchups AS (
            SELECT t.name, u.usage, e1.multiplier * coalesce(e2.multiplier, 1) AS multiplier
            FROM u
            JOIN pokemon p ON p.id = u.pokemon_id
            CROSS JOIN "type" t
            JOIN type_effect e1 ON e1.attacking_type_id = t.id AND e1.defending_type_id = p.type_1_id
            LEFT JOIN type_effect e2 ON e2.attacking_type_id = t.id AND e2.defending_type_id = p.type_2_id
            WHERE t.name <> 'stellar'
        )
        SELECT name,
               100 * sum(usage) FILTER (WHERE multiplier >= 2) / sum(usage) AS super_effective,
               100 * sum(usage) FILTER (WHERE multiplier < 1) / sum(usage) AS resisted
        FROM matchups
        GROUP BY name
        ORDER BY super_effective DESC
    """, **params()).fillna(0)

    bars(hits, "super_effective", "name", "% dos Pokémon usados atingidos de forma super efetiva",
         tooltip=[alt.Tooltip("resisted:Q", title="Resistido ou imune (%)", format=".1f")])
    st.caption("Apenas pela tabela de tipos: habilidades (ex.: Levitate) e Tera types não são consideradas.")


def speed_tiers() -> None:
    n = st.slider("Pokémon mais usados", 10, 50, 30, key="meta_speed_n")

    # Most common spread of each Pokémon, with the speed effect of its nature
    spreads = query("""
        WITH u AS (
            SELECT u.usage_id, u.usage, p.name, p.speed AS base_speed
            FROM usage u JOIN pokemon p ON p.id = u.pokemon_id
            WHERE u.date = :date AND u.category_id = :category_id AND u.rating = :rating
            ORDER BY u.usage DESC LIMIT :n
        ),
        best AS (
            SELECT DISTINCT ON (s.usage_id) s.usage_id, s.nature_id, s.speed_ev
            FROM usage_spread s JOIN u USING (usage_id)
            ORDER BY s.usage_id, s.weight DESC
        )
        SELECT u.name, u.base_speed, b.speed_ev, initcap(n.name) AS nature,
               CASE WHEN plus.name = 'speed' THEN 110 WHEN minus.name = 'speed' THEN 90 ELSE 100 END AS nature_pct
        FROM u
        JOIN best b USING (usage_id)
        JOIN nature n ON n.id = b.nature_id
        LEFT JOIN stat plus ON plus.id = n.increased_stat_id
        LEFT JOIN stat minus ON minus.id = n.decreased_stat_id
    """, n=n, **params())

    # Level 100, 31 IVs: floor((2 * base + 31 + EV / 4) + 5), then the nature (integer math, as in the games)
    raw = 2 * spreads["base_speed"] + 31 + spreads["speed_ev"] // 4 + 5
    spreads["speed"] = raw * spreads["nature_pct"] // 100
    spreads["nature_effect"] = spreads["nature_pct"].map({110: "Natureza +Velocidade", 100: "Natureza neutra", 90: "Natureza −Velocidade"})

    chart = alt.Chart(spreads).mark_circle(size=90).encode(
        x=alt.X("speed:Q", title="Velocidade (nível 100, spread mais comum)", scale=alt.Scale(zero=False)),
        y=alt.Y("name:N", sort="-x", title=None),
        color=alt.Color("nature_effect:N", title=None, legend=alt.Legend(orient="bottom")),
        tooltip=[alt.Tooltip("name:N", title=" "), alt.Tooltip("speed:Q", title="Velocidade"), alt.Tooltip("base_speed:Q", title="Base"),
                 alt.Tooltip("nature:N", title="Natureza"), alt.Tooltip("speed_ev:Q", title="EVs de velocidade")],
    )
    st.altair_chart(chart.properties(height=26 * len(spreads)), width="stretch")
    st.caption("Sem boosts, itens (Choice Scarf) ou habilidades. Pokémon com a mesma velocidade empatam.")


def move_classes() -> None:
    split = query(METAGAME_TOTALS + """
        SELECT dc.name AS damage_class, sum(u.usage * x.weight / total.total) AS weight
        FROM usage_move x
        JOIN u USING (usage_id) JOIN total USING (usage_id)
        JOIN move m ON m.id = x.move_id
        JOIN damage_class dc ON dc.id = m.damage_class_id
        GROUP BY dc.name
    """, **params())

    split["share"] = 100 * split["weight"] / split["weight"].sum()
    split["damage_class"] = split["damage_class"].map({"physical": "Físico", "special": "Especial", "status": "Status"})
    bars(split, "share", "damage_class", "% de todos os slots de golpe")


def priority_moves() -> None:
    moves = query(METAGAME_TOTALS + """
        SELECT m.name, m.priority, 100 * sum(u.usage * x.weight / total.total) / (SELECT sum(usage) FROM u) AS share
        FROM usage_move x
        JOIN u USING (usage_id) JOIN total USING (usage_id)
        JOIN move m ON m.id = x.move_id
        WHERE m.priority > 0
        GROUP BY m.name, m.priority
        ORDER BY share DESC
        LIMIT 15
    """, **params())

    bars(moves, "share", "name", "% dos Pokémon usados que o carregam", tooltip=[alt.Tooltip("priority:Q", title="Prioridade")])


def legendaries() -> None:
    kinds = query(METAGAME_TOTALS + """
        SELECT CASE WHEN s.is_mythical THEN 'Mítico' WHEN s.is_legendary THEN 'Lendário' ELSE 'Comum' END AS kind,
               100 * sum(u.usage) / (SELECT sum(usage) FROM u) AS share
        FROM u JOIN pokemon p ON p.id = u.pokemon_id JOIN species s ON s.id = p.species_id
        GROUP BY 1
    """, **params())

    bars(kinds, "share", "kind", "% de todas as escolhas")


def generations() -> None:
    gens = query(METAGAME_TOTALS + """
        SELECT 'Geração ' || s.generation AS generation, 100 * sum(u.usage) / (SELECT sum(usage) FROM u) AS share
        FROM u JOIN pokemon p ON p.id = u.pokemon_id JOIN species s ON s.id = p.species_id
        GROUP BY s.generation
    """, **params())

    chart = alt.Chart(gens).mark_bar().encode(
        x=alt.X("generation:N", sort=[f"Geração {g}" for g in range(1, 10)], title=None),
        y=alt.Y("share:Q", title="% de todas as escolhas"),
        tooltip=[alt.Tooltip("generation:N", title=" "), alt.Tooltip("share:Q", title="% das escolhas", format=".1f")],
    )
    st.altair_chart(chart, width="stretch")
    st.caption("Geração em que a espécie foi introduzida (formas regionais contam como a sua espécie).")


def eviolite() -> None:
    nfe = query(METAGAME_TOTALS + """
        SELECT p.name, 100 * u.usage AS usage_pct, coalesce(100 * x.weight / total.total, 0) AS eviolite_pct
        FROM u
        JOIN pokemon p ON p.id = u.pokemon_id
        JOIN total USING (usage_id)
        LEFT JOIN usage_item x ON x.usage_id = u.usage_id AND x.item_id = (SELECT id FROM item WHERE name = 'eviolite')
        WHERE NOT p.is_fully_evolved
        ORDER BY u.usage DESC
    """, **params())

    st.metric("Pokémon não totalmente evoluídos usados", len(nfe), help=f"{nfe['usage_pct'].sum() / 6:.1f}% de todas as escolhas")
    bars(nfe.head(15), "eviolite_pct", "name", "% dos seus sets com Eviolite",
         tooltip=[alt.Tooltip("usage_pct:Q", title="Uso (%)", format=".2f")])
    st.caption("Os 15 Pokémon não totalmente evoluídos mais usados neste metagame.")


QUESTIONS = {
    "tipos":      ("Quais tipos dominam o meta?", types),
    "cobertura":  ("Quais tipos de ataque acertam o meta de forma super efetiva?", coverage),
    "velocidade": ("Quais são os speed tiers do meta?", speed_tiers),
    "classes":    ("Como se dividem os golpes físicos, especiais e de status?", move_classes),
    "prioridade": ("Quais golpes de prioridade são os mais usados?", priority_moves),
    "lendarios":  ("Que parcela do meta é lendária ou mítica?", legendaries),
    "geracoes":   ("De qual geração vêm os Pokémon usados?", generations),
    "eviolite":   ("Quais Pokémon não totalmente evoluídos são usados com Eviolite?", eviolite),
}

from_link("meta_question", QUESTIONS)

question = st.selectbox("Pergunta", list(QUESTIONS), format_func=lambda key: QUESTIONS[key][0], key="meta_question")
QUESTIONS[question][1]()

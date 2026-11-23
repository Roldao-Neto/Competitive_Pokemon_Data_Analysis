import streamlit as st

from charts import bars, view
from db import describe, params, query
from queries import METAGAME_TOTALS

st.title("Cores e matchups")
st.caption(describe())

choice = view({"duplas": "Duplas mais comuns", "respostas": "Respostas às maiores ameaças"}, key="cores_view")

if choice == "duplas":
    # A pair's share of teams = usage of A x % of A's teams with B, averaged over both directions (A->B, B->A)
    pairs = query(METAGAME_TOTALS + """
        , directed AS (
            SELECT least(u.pokemon_id, x.teammate_id) AS a, greatest(u.pokemon_id, x.teammate_id) AS b,
                   u.usage * x.weight / total.total AS share
            FROM usage_teammate x JOIN u USING (usage_id) JOIN total USING (usage_id)
            WHERE x.teammate_id <> u.pokemon_id
        )
        SELECT pa.name || ' + ' || pb.name AS pair, 100 * avg(share) AS teams_pct
        FROM directed
        JOIN pokemon pa ON pa.id = directed.a
        JOIN pokemon pb ON pb.id = directed.b
        GROUP BY pa.name, pb.name
        ORDER BY teams_pct DESC
        LIMIT 50
    """, **params())

    n = st.slider("Quantas", 5, 30, 15, key="cores_n")
    bars(pairs.head(n), "teams_pct", "pair", "% dos times com os dois")

else:
    n = st.slider("Maiores ameaças", 5, 15, 10, key="cores_threats")
    answers = query("""
        WITH threats AS (
            SELECT usage_id, pokemon_id, usage FROM usage
            WHERE date = :date AND category_id = :category_id AND rating = :rating
            ORDER BY usage DESC LIMIT :n
        ),
        ranked AS (
            SELECT c.usage_id, p.name, 100 * (c.p - 4 * c.d) AS score,
                   row_number() OVER (PARTITION BY c.usage_id ORDER BY c.p - 4 * c.d DESC) AS position
            FROM usage_check_counter c JOIN threats USING (usage_id) JOIN pokemon p ON p.id = c.counter_id
        )
        SELECT pt.name AS threat, 100 * t.usage AS usage_pct, r.position, r.name || ' (' || round(r.score::numeric, 1) || ')' AS answer
        FROM threats t
        JOIN pokemon pt ON pt.id = t.pokemon_id
        LEFT JOIN ranked r ON r.usage_id = t.usage_id AND r.position <= 3
        ORDER BY t.usage DESC, r.position
    """, n=n, **params())

    table = answers.pivot_table(index=["threat", "usage_pct"], columns="position", values="answer", aggfunc="first")
    table = table.reindex(columns=[1, 2, 3]).reset_index().sort_values("usage_pct", ascending=False)
    table.columns = ["Ameaça", "Uso (%)", "Melhor resposta", "2ª", "3ª"]

    st.dataframe(table.fillna("—"), hide_index=True,
                 column_config={"Uso (%)": st.column_config.NumberColumn(format="%.1f")})
    st.caption("Respostas ordenadas pela pontuação de counter do Smogon (entre parênteses): chance de a ameaça ser "
               "nocauteada ou forçada a trocar no confronto, menos 4 desvios padrão.")

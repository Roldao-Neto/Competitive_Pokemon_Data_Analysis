import streamlit as st

# The README questions, each linking to the page and view that answers it best: (question, page, view)
SECTIONS = {
    "Uso e tendências": [
        ("Quais Pokémon são os mais usados em cada tier, rating e mês?", "views/usage.py", "mais_usados"),
        ("Como o uso mudou nos 2 anos de gen9 (os que subiram, os que caíram e os que chegaram)?", "views/trends.py", "altas_quedas"),
        ("Quantas batalhas são jogadas em cada tier ao longo do tempo?", "views/trends.py", "batalhas"),
    ],
    "Diferença de habilidade": [
        ("O que os jogadores do topo do ladder usam em comparação com todos (rating 0 contra 1760/1825)?", "views/skill_gap.py", "todos_vs_topo"),
        ("Em quais Pokémon os melhores jogadores confiam (Viability Ceiling / GXE)?", "views/skill_gap.py", "teto"),
    ],
    "Sets": [
        ("Quais são as habilidades, itens, golpes, Tera types e spreads (natureza + EVs) mais comuns de cada Pokémon, e como eles mudaram?",
         "views/pokemon.py", "habilidades"),
        ("Quais são os itens, golpes (como Stealth Rock e remoção de hazards) e Tera types mais usados no meta inteiro?", "views/sets.py", "itens"),
    ],
    "Cores e matchups": [
        ("Quais duplas de Pokémon são mais usadas juntas?", "views/cores.py", "duplas"),
        ("Quais Pokémon são os melhores checks e counters para as maiores ameaças?", "views/cores.py", "respostas"),
    ],
    "Combinadas com a PokeAPI": [
        ("Quais tipos dominam o meta, e quais tipos de ataque o acertam de forma super efetiva?", "views/meta.py", "tipos"),
        ("Quais são os speed tiers do meta (velocidade base + natureza + EVs dos spreads)?", "views/meta.py", "velocidade"),
        ("Como se dividem os golpes físicos, especiais e de status, e quais golpes de prioridade são os mais usados?", "views/meta.py", "classes"),
        ("Que parcela do meta é lendária/mítica, e de qual geração vêm os Pokémon usados?", "views/meta.py", "lendarios"),
        ("Quais Pokémon que não estão totalmente evoluídos são usados com Eviolite?", "views/meta.py", "eviolite"),
    ],
}

st.title("Perguntas norteadoras")
st.caption("As estatísticas do Smogon são agregados mensais por tier e corte de rating: as perguntas respondem "
           "**o que é usado, por quem e com o quê**, não **o que vence**. Clique em uma pergunta para abrir a resposta "
           "com o tier, o mês e o rating escolhidos na barra lateral.")

for section, questions in SECTIONS.items():
    st.subheader(section)

    for question, page, view in questions:
        st.page_link(page, label=question, icon=":material/arrow_forward:", query_params={"view": view})

st.subheader("O que os dados não respondem")
st.markdown(
    "- Taxas de vitória de Pokémon, sets, times ou tipos: não há resultados de batalha (o GXE mede os jogadores, não os Pokémon)\n"
    "- Times completos ou arquétipos: os teammates só trazem pares\n"
    "- Sets completos: habilidades, itens e golpes são contados separadamente\n"
    "- Qualquer coisa por batalha, por jogador ou mais detalhada que um mês"
)

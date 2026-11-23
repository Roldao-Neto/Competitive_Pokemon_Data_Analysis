import streamlit as st

from charts import bars, view
from db import describe, params
from queries import meta_share

HAZARDS = ["stealthrock", "spikes", "toxicspikes", "stickyweb", "defog", "rapidspin", "mortalspin", "tidyup", "courtchange"]

st.title("Sets")
st.caption(describe())

kind = view({"itens": "Itens", "golpes": "Golpes", "tera": "Tera types", "habilidades": "Habilidades"}, key="sets_view")
share = meta_share(kind, **params())

if kind == "golpes" and st.toggle("Apenas entry hazards e remoção de hazards", key="sets_hazards"):
    share = share[share["name"].isin(HAZARDS)]
else:
    n = st.slider("Quantos", 5, 40, 15, key="sets_n")
    share = share.head(n)

bars(share, "share", "name", "% dos Pokémon usados que o carregam")
st.caption("Cada Pokémon conta pelo seu uso: um item em 50% dos sets de um Pokémon usado em 20% dos times pesa tanto "
           "quanto um item em 100% dos sets de um Pokémon usado em 10%.")

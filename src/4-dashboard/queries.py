"""Queries shared by several pages. Percentages follow Smogon:

- usage_pct: share of teams that use the Pokémon (sums to ~600% per metagame, 6 Pokémon per team)
- entry pct: weight of an ability / item / move / ... divided by the Pokémon's total weight (sum of its ability weights)
- meta-wide share: sum over Pokémon of usage x entry pct, divided by the total usage = % of the Pokémon used that carry it
"""

import pandas as pd

from db import query

# Usage rows of the selected metagame + total weight of each Pokémon (its ability weights)
METAGAME_TOTALS = """
    WITH u AS (
        SELECT usage_id, pokemon_id, usage
        FROM usage
        WHERE date = :date AND category_id = :category_id AND rating = :rating
    ),
    total AS (
        SELECT a.usage_id, sum(a.weight) AS total
        FROM usage_ability a JOIN u USING (usage_id)
        GROUP BY a.usage_id
    )
"""

# Nested Smogon entries: table, join to its names, label shown
ENTRIES = {
    "habilidades":  ("usage_ability",   "JOIN ability e ON e.id = x.ability_id",  "e.name"),
    "itens":        ("usage_item",      "JOIN item e ON e.id = x.item_id",        "e.name"),
    "golpes":       ("usage_move",      "JOIN move e ON e.id = x.move_id",        "e.name"),
    "tera":         ("usage_tera_type", 'JOIN "type" e ON e.id = x.type_id',      "e.name"),
    "spreads":      ("usage_spread",    "JOIN nature e ON e.id = x.nature_id",
                     "initcap(e.name) || ' ' || concat_ws('/', x.hp_ev, x.attack_ev, x.defense_ev, x.special_attack_ev, x.special_defense_ev, x.speed_ev)"),
    "companheiros": ("usage_teammate",  "JOIN pokemon e ON e.id = x.teammate_id", "e.name"),
}


def metagame_usage(category_id: int, date, rating: int) -> pd.DataFrame:
    df = query("""
        SELECT u.usage_id, p.id AS pokemon_id, p.name, 100 * u.usage AS usage_pct, u.raw_count,
               u.viability_players, u.viability_top_gxe, u.viability_99th_gxe, u.viability_95th_gxe
        FROM usage u JOIN pokemon p ON p.id = u.pokemon_id
        WHERE u.date = :date AND u.category_id = :category_id AND u.rating = :rating
        ORDER BY u.usage DESC
    """, category_id=category_id, date=date, rating=rating)

    return df.assign(rank=range(1, len(df) + 1))


def tier_history(category_id: int, rating: int) -> pd.DataFrame:
    return query("""
        SELECT u.date, p.name, 100 * u.usage AS usage_pct
        FROM usage u JOIN pokemon p ON p.id = u.pokemon_id
        WHERE u.category_id = :category_id AND u.rating = :rating
        ORDER BY u.date, u.usage DESC
    """, category_id=category_id, rating=rating)


def pokemon_entries(kind: str, pokemon_id: int, category_id: int, rating: int, date=None) -> pd.DataFrame:
    """% of one Pokémon's sets per entry, for the selected month or (date=None) for every month."""
    table, join, label = ENTRIES[kind]
    month_filter = "AND date = :date" if date is not None else ""

    return query(f"""
        WITH u AS (
            SELECT usage_id, date FROM usage
            WHERE pokemon_id = :pokemon_id AND category_id = :category_id AND rating = :rating {month_filter}
        ),
        total AS (
            SELECT a.usage_id, sum(a.weight) AS total FROM usage_ability a JOIN u USING (usage_id) GROUP BY a.usage_id
        )
        SELECT u.date, {label} AS name, 100 * x.weight / total.total AS pct
        FROM {table} x JOIN u USING (usage_id) JOIN total USING (usage_id) {join}
        ORDER BY u.date, pct DESC
    """, pokemon_id=pokemon_id, category_id=category_id, rating=rating, **({"date": date} if date is not None else {}))


def meta_share(kind: str, category_id: int, date, rating: int) -> pd.DataFrame:
    table, join, label = ENTRIES[kind]

    return query(METAGAME_TOTALS + f"""
        SELECT {label} AS name, 100 * sum(u.usage * x.weight / total.total) / (SELECT sum(usage) FROM u) AS share
        FROM {table} x JOIN u USING (usage_id) JOIN total USING (usage_id) {join}
        GROUP BY 1
        ORDER BY share DESC
    """, category_id=category_id, date=date, rating=rating)


def counters(usage_id: int) -> pd.DataFrame:
    """Smogon's checks and counters: score = KO-or-switch chance - 4 standard deviations."""
    return query("""
        SELECT p.name, c.n, 100 * c.p AS ko_or_switch_pct, 100 * c.d AS std_pct, 100 * (c.p - 4 * c.d) AS score
        FROM usage_check_counter c JOIN pokemon p ON p.id = c.counter_id
        WHERE c.usage_id = :usage_id
        ORDER BY score DESC
    """, usage_id=usage_id)

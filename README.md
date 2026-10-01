# Competitive_Pokemon_Data_Analysis

This is a University Project of Data Engineering where I use the following datasets:

- [Smogon Stats on Pokemon Showdown](https://www.smogon.com/stats/): for competitive pokemon metadata
- [PokeAPI](https://pokeapi.co/): for other Pokemon data

Its goal is to analyse the Competitive Pokemon scenario and look for useful information about the gen9 meta.

## Project Structure

This project follows a medallion architecture (bronze/silver/gold), mirrored between `data/` (storage) and `src/` (processing code per layer).

```
Competitive_Pokemon_Data_Analysis/
├── data/
│   ├── 1-bronze/                   # raw extracted data (Smogon + PokeAPI)
│   │   ├── PokeAPI/
│   │   │   └── <endpoint>/         # <endpoint>_<id>.json, one file per resource
│   │   └── Smogon/
│   │       └── <year>/<month>/     # gen9<tier>-<rating cutoff>.json
│   ├── 2-silver/                   # cleaned/transformed data
│   └── 3-gold/                     # final/analysis-ready data
├── src/
│   ├── 1-bronze/
│   │   ├── pokeapi_ingestion.py    # pokeapi data extraction code
│   │   └── smogon_ingestion.py     # smogon data extraction code
│   ├── 2-silver/
│   └── 3-gold/
├── pyproject.toml                  # project deps, use uv for easy sync
├── uv.lock
├── LICENSE
└── README.md
```

## How to run

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cd src/1-bronze
uv run python smogon_ingestion.py
uv run python pokeapi_ingestion.py
```

- The scripts resolve `data/` relative to the current directory, so they must be run from inside their own `src/<layer>/` folder.
- The data is not versioned (~4.5 GB in the bronze layer alone), so it has to be downloaded by running the scripts.
- Both scripts skip files that were already downloaded, so they can be interrupted and re-run, and re-running them later only fetches new data (e.g. a new Smogon month).

## Decisions made

- All timestamps are going to be UTC
- Only gen9 data is used, from 2024-08 onwards: PokeAPI only represents the current state of the games, so older generations would not match it
- Smogon tiers used: Anything Goes, Ubers, UbersUU, OU, UU, RU, NU, PU and ZU (formats like hackmons are left out)
- Smogon data comes from the `chaos` stats, which have 4 files per tier and month, one per rating cutoff
- PokeAPI endpoints used: `ability`, `item`, `move`, `nature`, `pokemon`, `pokemon-species` and `type`
- Both sources are community servers, so the download loops wait between requests in order to not flood them
- Smogon `chaos` stats are monthly aggregates: there is no per-battle data (teams per player, winners)

## Questions the data can answer

Smogon's `chaos` stats are monthly aggregates per tier and rating cutoff, so the analysis answers **what is used, by whom and with what**, not **what wins**.

### Usage and trends
- Which Pokémon are the most used in each tier, rating and month?
- How did usage change over the 2 years of gen9 (risers, fallers, newcomers)?
- Which Pokémon moved between tiers (e.g. after a ban)?
- How many battles are played in each tier over time?

### Skill gap
- What do high-ladder players use compared to everyone (rating 0 vs 1760/1825)?
- Which Pokémon are trusted by the best players (Viability Ceiling / GXE)?

### Sets
- What are the most common abilities, items, moves, Tera types and spreads (nature + EVs) of each Pokémon, and how did they change?
- What are the most used items, moves (e.g. Stealth Rock and hazard removal) and Tera types in the whole meta?

### Cores and matchups
- Which Pokémon pairs are used together the most?
- Which Pokémon are the best checks and counters to the top threats?

### Combined with PokeAPI
- Which types dominate the meta, and which attacking types hit it super-effectively?
- What are the speed tiers of the meta (base speed + nature + EVs from the spreads)?
- How are physical, special and status moves split, and which priority moves are the most used?
- What share of the meta is legendary/mythical, and from which generation do the used Pokémon come?
- Which not fully evolved Pokémon are used with Eviolite?

### What it can't answer
- Win rates of Pokémon, sets, teams or types: there are no battle results (GXE measures the players, not the Pokémon)
- Full teams or archetypes: Teammates only gives pairs
- Complete sets: abilities, items and moves are counted separately
- Anything per battle, per player or finer than a month

## License

Apache License 2.0

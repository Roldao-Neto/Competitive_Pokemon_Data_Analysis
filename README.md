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

## License

Apache License 2.0

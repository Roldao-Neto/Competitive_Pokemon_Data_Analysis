# Competitive_Pokemon_Data_Analysis

This is an University Project of Data Engineering where I use the following datasets:

- [Smogon Stats on Pokemon Showdown](https://www.smogon.com/stats/): for competitive pokemon metadata
- [PokeAPI](https://pokeapi.co/): for other Pokemon data

## Project Structure

This project follows a medallion architecture (bronze/silver/gold), mirrored between `data/` (storage) and `src/` (processing code per layer).

```
Competitive_Pokemon_Data_Analysis/
├── data/
│   ├── 1-bronze/               # raw extracted data (Smogon + PokeAPI)
│   ├── 2-silver/               # cleaned/transformed data
│   └── 3-gold/                 # final/analysis-ready data
├── src/
│   ├── 1-bronze/
│   │   └── data_extractor.py   # extracts raw data from Smogon & PokeAPI (rate-limited)
│   ├── 2-silver/
│   └── 3-gold/
├── pyproject.toml              # project deps, use uv for easy sync
├── uv.lock
├── LICENSE
└── README.md
```

## Decisions made

- All timestamps are going to be UTC

## Licence

Apache License 2.0

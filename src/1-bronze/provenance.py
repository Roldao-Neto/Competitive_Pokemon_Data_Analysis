# Provenance of the Bronze Layer: the data itself is not versioned (~4.5 GB), so this script writes a small CSV
# that is committed instead. It records, for every downloaded file, where it came from (source URL), its content
# fingerprint (SHA-256 + size) and when it was written to disk. Re-run it after every new download.

# %% Imports

import csv
import hashlib
from datetime import UTC, datetime
from pathlib import Path

from tqdm import tqdm

# %% Global Variables

DATA_PATH   = Path(Path.cwd().parent.parent, 'data')
BRONZE_PATH = Path(DATA_PATH / '1-bronze')

PROVENANCE_FILE = Path(BRONZE_PATH / 'provenance.csv')

POKEAPI            = "https://pokeapi.co/api/v2/"
SMOGON_DATASET_URL = "https://www.smogon.com/stats/"

# %% Global Functions

def source_url(file: Path) -> tuple[str, str]:
    parts = file.relative_to(BRONZE_PATH).parts

    if parts[0] == "PokeAPI":
        # PokeAPI/<endpoint>/<endpoint>_<id>.json -> https://pokeapi.co/api/v2/<endpoint>/<id>/
        endpoint = parts[1]
        id = file.stem.removeprefix(f"{endpoint}_")
        return "PokeAPI", f"{POKEAPI}{endpoint}/{id}/"

    # Smogon/<year>/<month>/<name>.json -> https://www.smogon.com/stats/<year>-<month>/chaos/<name>.json
    (_, year, month, name) = parts
    return "Smogon", f"{SMOGON_DATASET_URL}{year}-{month}/chaos/{name}"

def sha256(file: Path) -> str:
    with file.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

# %% Building the provenance table

files = sorted(BRONZE_PATH.rglob('*.json'))

rows: list[dict[str, str | int]] = []

for file in tqdm(files):
    (source, url) = source_url(file)
    stat = file.stat()

    rows.append({
        "source":            source,
        "path":              file.relative_to(DATA_PATH).as_posix(),
        "url":               url,
        "size_bytes":        stat.st_size,
        "sha256":            sha256(file),
        # The ingestion scripts do not log the download time, so the file modification time is used instead
        "file_modified_utc": datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(timespec='seconds'),
    })

# %% Writing it

with PROVENANCE_FILE.open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"{len(rows)} files written to {PROVENANCE_FILE}")

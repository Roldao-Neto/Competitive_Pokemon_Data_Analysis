"""
First Step (1):
This script re-checks what the Silver Layer delivers: the columns of every parquet.
The Result will be used to check all attributes again and model the DER for the SQL database.
"""
# %% Imports

from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# %% Global Variables

DATA_PATH   = Path(Path.cwd().parent.parent, 'data')
SILVER_PATH = Path(DATA_PATH / '2-silver')

PARQUETS = sorted(SILVER_PATH.rglob('*.parquet'))

# %% Global Functions

def arrow_to_pandas(table: pa.Table) -> pd.DataFrame:
    return table.to_pandas(types_mapper=lambda t: pd.ArrowDtype(t) if pa.types.is_list(t) else None)

# %% Printing the columns of every parquet (only the schema is read, not the data)

for file in PARQUETS:
    meta = pq.ParquetFile(file).metadata
    schema = pq.read_schema(file)

    print(f"{file.relative_to(SILVER_PATH)} | rows: {meta.num_rows} | columns: {len(schema)} | size: {file.stat().st_size / 2**20:.1f} MB")
    for field in schema:
        print(f"    {field.name:<20} {field.type}")
    print("----------")

# %% Reading every row of every parquet, without printing it

for file in PARQUETS:
    expected = pq.ParquetFile(file).metadata.num_rows

    print(f"{file.relative_to(SILVER_PATH)}:")
    for col in pq.read_schema(file).names:
        df = arrow_to_pandas(pq.read_table(file, columns=[col]))
        status = "OK" if len(df) == expected else f"MISSING {expected - len(df)} ROWS"

        print(f"    {col:<20} rows: {len(df):>7} | nulls: {df[col].isna().sum():>7} | dtype: {str(df[col].dtype)[:40]:<40} | {status}")
    print("----------")

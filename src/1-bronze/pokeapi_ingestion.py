# The Bronze Layer consists only of the code that is used to extract all the data from my data sources,
# which are smogon and pokeAPI. Since both of them are "community" servers with strict policies, and I will be
# downloading "a lot" of data, this code will have some timers in the download loop in order to not flood their
# server with requests. If you are going to run this code, please follow their policy as well.

# %% Imports

import time
from pathlib import Path
from typing import cast

import requests
from tqdm import tqdm  # pyright: ignore[reportMissingModuleSource]

# %% Global Variables

DATA_PATH   = Path(Path.cwd().parent.parent, 'data')
BRONZE_PATH = Path(DATA_PATH / '1-bronze')

POKEAPI = "https://pokeapi.co/api/v2/"

DESIRED_ENDPOINTS = [
    "ability",
    "item",
    "move",
    "nature",
    "pokemon",
    "pokemon-species",
    "type"
]

# %% Global Functions

def await_response(url: str, sleep_time: int=10) -> requests.Response:
    r = requests.get(url=url)

    while (r.status_code in {429, 500, 502, 503, 504}):
        time.sleep(sleep_time)
        r = requests.get(url=url)

    return r

# %% Getting and printing all available endpoints:

endpoints = cast(dict[str, str], await_response(POKEAPI).json())

for i, value in endpoints.items():
    print(f"{i}: {value}")

# %% Meta of this code: {"deploy_date":"1790465154","hash":"168b1e89467054cda2e7df43ccebbb69b459497a","tag":null}

r = await_response(f"{POKEAPI}meta")
print(r.text)

# %% Analysing the API Structure and creating dict:

count_endpoint = {}

for i in DESIRED_ENDPOINTS:
    print(f"{i}:")
    r = cast(dict[str, str], await_response(f"{POKEAPI}{i}").json())
    print(r.keys())
    print(f"count: {r["count"]}")
    print(f"len: {len(r["results"])}")
    print("----------")

    count_endpoint[i] = r["count"]
    
    time.sleep(1)

# %% Downloading JSONs

for endpoint in DESIRED_ENDPOINTS:
    r = await_response(f"{POKEAPI}{endpoint}?limit={count_endpoint[endpoint]}")
    download_urls = [x["url"] for x in r.json()["results"]]
    
    for url in tqdm(download_urls):
        # https://pokeapi.co/api/v2/ability/1/
        id = url.rstrip("/").rsplit("/", 1)[-1]
        
        file = Path(BRONZE_PATH, "PokeAPI", endpoint, f"{endpoint}_{id}.json")
        
        file.parent.mkdir(parents=True, exist_ok=True)
        if file.exists():
            continue

        r = await_response(url)
        file.write_bytes(r.content)
        
        time.sleep(0.5)

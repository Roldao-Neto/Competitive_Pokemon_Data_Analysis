# The Bronze Layer consists only of the code that is used to extract all the data from my data sources,
# which are smogon and pokeAPI. Since both of them are "community" servers with strict policies, and I will be
# downloading "a lot" of data, this code will have some timers in the download loop in order to not flood their
# server with requests. If you are going to run this code, please follow their policy as well.

# %% Imports

import re
import time
from pathlib import Path

import requests
from tqdm import tqdm  # pyright: ignore[reportMissingModuleSource]

# %% Global Variables

DATA_PATH   = Path(Path.cwd().parent.parent, 'data')
BRONZE_PATH = Path(DATA_PATH / '1-bronze')
SILVER_PATH = Path(DATA_PATH / '2-silver')
GOLD_PATH   = Path(DATA_PATH / '3-gold')

SMOGON_DATASET_URL = "https://www.smogon.com/stats/"

DESIRED_CATEGORIES: list[str] = [
    "anythinggoes",  # - Anything Goes:    No bans
    "ubers",         # - Ubers:            Gets what has been banned from OU for being too strong
    "ubersuu",
    "ou",            # - OU (OverUsed):    Main tier
    "uu",            # - UU (UnderUsed):   Legal Pokémon in OU but that are not that used
    "ru",            # - RU (RarelyUsed):  Less used that UU
    "nu",            # - NU (NeverUsed):   Less used than RU
    "pu",            # - PU:               Less used than NU
    "zu"             # - ZU (ZeroUsed):    Less used than PU
]

TIME_FILTER = (2024, 8)

# %% Global Functions

def await_response(url: str, sleep_time: int=10) -> requests.Response:
    r = requests.get(url=url)

    while (r.status_code in {429, 500, 502, 503, 504}):
        time.sleep(sleep_time)
        r = requests.get(url=url)

    return r

# %% Getting Available Dates and Filtering

# The current generation of Pokémon is gen 9, so I decided to get data from 2024-08 to the current month (2026-08) -> ~2 years of data of gen 9 battles.

# This decision had to be made because pokeAPI (as far as I know) do not have historical data from the previous gens: the data returned from the API represents the current state of the game.

r = await_response(SMOGON_DATASET_URL)

dates: list[str] = re.findall(r'<a href="([^"/]+)/">', r.text)

dates_url: list[str] = []

for i in range(len(dates)):
    try:
        year  = int(dates[i][:4])
        month = int(dates[i][5:7])

        if (year, month) >= TIME_FILTER:
            dates_url.append(SMOGON_DATASET_URL + dates[i] + '/chaos/')
    except ValueError:
        continue

# %% Getting Gen 9 data from each month and downloading it

# Pokemon Showndown (the website that smogon extracts that from) has many types of battle inside gen9 battles, for this analysis, I am not interested in many of them: hackmons for example.

download_urls: list[str] = []

for item in dates_url:
    r = await_response(item)
    
    gen9_data: list[str] = re.findall(r'<a href="(gen9[^"/]+.json)">', r.text)
    
    for i in gen9_data:
        for j in DESIRED_CATEGORIES:
            if f"gen9{j}-" in i:
                download_urls.append(f"{item}{i}")
                break

    time.sleep(1)

# %% Finally, downloading each one of them for all the years:

for i in tqdm(download_urls):
    (year, month) = re.search(r"\d{4}-\d{2}", i).group().split('-')  # pyright: ignore[reportOptionalMemberAccess]
    name = re.search(r'(gen9[^"/]+.json)', i).group()  # pyright: ignore[reportOptionalMemberAccess]

    file = Path(BRONZE_PATH, "Smogon", year, month, name)
    
    file.parent.mkdir(parents=True, exist_ok=True)
    
    if file.exists():
        continue

    r = await_response(i)
    file.write_bytes(r.content)  # pyright: ignore[reportUnusedCallResult]
    
    time.sleep(1)

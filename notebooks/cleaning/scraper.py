import json
def narf_html(resp):
    txt = resp.text
    if txt.lstrip().startswith("{"):
        try:
            payload = resp.json()
            return payload.get("content") or payload.get("html") or payload.get("data") or txt
        except Exception:
            return txt
    return txt


import os, re, json, time
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qsl, urlencode, urlunparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from io import StringIO

COLS = [
"pi","ae","hi","wi","pf","oa","bo","bp","vl","wg","ta","cr","fi","he","sh","vo","ts",
"dr","cu","fr","lo","bl","to","ac","sp","ag","re","ba","tp","so","ju","st","ln","te",
"ar","in","po","vi","pe","cm","td","ma","sa","sl","tg","gd","gh","gc","gp","gr"
]

def safe_name(s: str) -> str:
    s = re.sub(r'[\\/:*?"<>|]+', '-', str(s))
    s = re.sub(r'\s+', '-', s).strip('-')
    return s

def add_columns_to_url(u: str, cols) -> str:
    pu = urlparse(u)
    pairs = parse_qsl(pu.query, keep_blank_values=True)
    pairs += [("showCol[]", c) for c in cols]
    return urlunparse(pu._replace(query=urlencode(pairs, doseq=True)))

# ---- setup ----
all_roster_urls = pd.read_csv("all_roster_urls_post041026.csv")

session = requests.Session()
retry = Retry(
    total=4, backoff_factor=0.7,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
session.mount("https://", HTTPAdapter(max_retries=retry))

API = "jorXNk0XeOjcNxNdmsBHa9YXUKSwnSgMFChONEcLZh4UVsc12swTZjUE2rgfKdEgb1L7KEdEs84IhmobWb"
base_url = "https://sofifa.com"

OUTPUT_DIR = "G:/My Drive/GitHubProjects/MLS/data/raw/players/players_2"
os.makedirs(OUTPUT_DIR, exist_ok=True)
existing_files = set(os.listdir(OUTPUT_DIR))

count = 0

for rel in all_roster_urls["url"].dropna():
    print(f"Processing roster URL: {rel}")
    base = urljoin(base_url, rel)
    scrape_url = add_columns_to_url(base, COLS)

    resp = session.get(
        "https://api.scrapingfish.com/api/v1/",
        params={"api_key": API, "url": scrape_url}
    )

    if resp.status_code != 200 or not resp.content:
        print("Bad response:", resp.status_code, "for", rel)
        continue

    soup = BeautifulSoup(resp.text, "html.parser")

    date = ""
    sel = soup.select_one("#select-roster option[selected]")
    if sel:
        date = sel.get_text(strip=True)
    date = safe_name(date)

    h1 = soup.select_one("h1")
    if not h1:
        print("No team header for:", rel)
        continue
    team = h1.get_text(strip=True)
    safe_team = safe_name(team)

    roster_id = rel.strip('/').split('/')[-1]
    filename = f"{safe_team}-{date}-{roster_id}.csv"
    if filename in existing_files:
        print(f"Skipping existing: {filename}")
        continue

    table = soup.select_one("table")
    if table is None:
        print("No table for:", rel)
        continue

    try:
        df = pd.read_html(StringIO(str(table)))[0]
    except Exception as e:
        print("read_html failed for:", rel, "err:", e)
        continue

    df["date"] = date
    df["team"] = team

    df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False)
    existing_files.add(filename)
    count += 1

    print(f"Saved {count} files...")

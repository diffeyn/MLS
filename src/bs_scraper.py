import os
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from datetime import datetime
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode



api_key = os.getenv("SECRET_API_KEY")

def get_soup(url):
    ### API Payload for teams scraping
    payload = {
        "api_key": api_key,
        "url": url,
    }

    response = requests.get("https://scraping.narf.ai/api/v1/", params=payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def scrape_team_table(soup):
    ### Parse HTML for teams table
    teams_table = soup.find('table')
    if teams_table is None:
        raise ValueError("No table found in the scraped HTML.")

    rows = teams_table.find_all('tr')
    if not rows or not rows[0].find_all('th'):
        raise ValueError("No header row found in the table.")

    ### Convert to DataFrame
    teams_data = []
    headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]

    for row in rows[1:]:
        cols = [td.get_text(strip=True) for td in row.find_all('td')]
        if cols:
            teams_data.append(cols)

    teams_df = pd.DataFrame(teams_data, columns=headers)
    
    date = soup.find('select', {'name': 'roster'})
    if date:
        date = date.find('option', selected=True).text.strip()
        safe_date = date.replace("/", "-").replace(":", "-").strip()
        teams_df['date'] = safe_date
    else:
        date = datetime.now().strftime("%Y-%m-%d")
        teams_df['date'] = date
        
    team_links = []
    
    for td in teams_table.find_all('td', class_='s20'):
        a = td.find('a', href=True)
        if a:
            team_links.append(a['href'])

    return teams_df, team_links
    

COLS = [
    "pi","ae","hi","wi","pf","oa","bo","bp","vl","wg","ta","cr","fi","he","sh","vo","ts",
    "dr","cu","fr","lo","bl","to","ac","sp","ag","re","ba","tp","so","ju","st","ln","te",
    "ar","in","po","vi","pe","cm","td","ma","sa","sl","tg","gd","gh","gc","gp","gr"
]

def add_columns_to_url(u: str, cols) -> str:
    pu = urlparse(u)
    pairs = parse_qsl(pu.query, keep_blank_values=True)
    pairs += [("showCol[]", c) for c in cols]
    return urlunparse(pu._replace(query=urlencode(pairs, doseq=True)))

def extract_players(team_links):
    all_players = []

    for link in team_links:
        team_url = f"https://sofifa.com{link}"
        
        team_url = add_columns_to_url(team_url, COLS)
        
        soup = get_soup(team_url)
        
        ### Parse HTML for players table
        players_table = soup.find('table')
        if players_table is None:
            print(f"No table found for team URL: {team_url}")
            continue
        
        rows = players_table.find_all('tr')
        if not rows or not rows[0].find_all('th'):
            print(f"No header row found in the table for team URL: {team_url}")
            continue

        headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]
        for row in rows[1:]:
            cols = [td.get_text(strip=True) for td in row.find_all('td')]
            if cols:
                player_data = dict(zip(headers, cols))
                all_players.append(player_data)

    ### Convert to DataFrame
    players_df = pd.DataFrame(all_players)

    ## add safe_date column
    date = soup.find('select', {'name': 'roster'})
    if date:
        date = date.find('option', selected=True).text.strip()
        safe_date = date.replace("/", "-").replace(":", "-").strip()
        players_df['date'] = safe_date
    else:
        date = datetime.now().strftime("%Y-%m-%d")
        players_df['date'] = date
    
    print(f'colnames: {players_df.columns.tolist()}')
    
    return players_df
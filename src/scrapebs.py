import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

API_KEY = os.getenv("SCRAPER_API_KEY")

if not API_KEY:
    raise ValueError("SCRAPER_API_KEY environment variable not set.")

target_url = "https://sofifa.com/teams?type=all&lg%5B0%5D=39&showCol%5B%5D=ti&showCol%5B%5D=fm&showCol%5B%5D=oa&showCol%5B%5D=at&showCol%5B%5D=md&showCol%5B%5D=df&showCol%5B%5D=cw&showCol%5B%5D=ps"
scraper_url = f"http://api.scraperapi.com/?api_key={API_KEY}&url={target_url}"

response = requests.get(scraper_url)
soup = BeautifulSoup(response.text, 'html.parser')

print("Scraped title:", soup.title.text)
print("First 500 chars:\n", response.text[:500])

table = soup.find('table')
if table is None:
    raise ValueError("No table found in the scraped HTML.")

rows = table.find_all('tr')
if not rows or not rows[0].find_all('th'):
    raise ValueError("No header row found in the table.")

data = []
headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]

for row in rows[1:]:
    cols = [td.get_text(strip=True) for td in row.find_all('td')]
    if cols:
        data.append(cols)

df = pd.DataFrame(data, columns=headers)

date = datetime.now().strftime("%Y-%m-%d")
df.to_csv(f'data/scraping/teams_{date}', index=False)


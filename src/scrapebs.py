import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

payload = {
  "api_key": "UpJrdQ6h7q3wvGPVbsaK9OwISr2ZzcPYw5R9KOrQ8G0CUJ7qNBrkPnvRwmErsvyiWeWQzLMkiaCiZtUgHK",
  "url": "https://sofifa.com/teams?type=all&lg%5B0%5D=39&showCol%5B%5D=ti&showCol%5B%5D=fm&showCol%5B%5D=oa&showCol%5B%5D=at&showCol%5B%5D=md&showCol%5B%5D=df&showCol%5B%5D=cw&showCol%5B%5D=ps",
}

response = requests.get("https://scraping.narf.ai/api/v1/", params=payload)
soup = BeautifulSoup(response.text, 'html.parser')



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

date = soup.find('select', {'name': 'roster'})
if date:
    date = date.find('option', selected=True).text.strip()
    safe_date = date.replace("/", "-").replace(":", "-").strip()
else:
    date = datetime.now().strftime("%Y-%m-%d")


df.to_csv(f'data/scraping/teams_{date}.csv', index=False)


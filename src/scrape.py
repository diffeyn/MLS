#!/usr/bin/env python3


import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import Select
from datetime import datetime
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def set_up_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox') 
    options.add_argument('--disable-dev-shm-usage')
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service = service, options=options)
    return driver


def go_to_page(url, driver):
    driver.get(url)
    return driver


def extact_teams_and_href(driver):
    teams = []
    team_headers = []
    hrefs = []
    try:
        table = driver.find_element(By.TAG_NAME, 'table')
        header_elements = table.find_elements(By.TAG_NAME, "th")
        for header in header_elements:
            team_headers.append(header.text.strip())
        rows = table.find_elements(By.XPATH, ".//tbody/tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            row_data = []
            for cell in cells:
                cell_text = cell.text.strip()
                row_data.append(cell_text)
                try:
                    link_element = cell.find_element(By.TAG_NAME, 'a')
                    hrefs.append(link_element.get_attribute('href'))
                except Exception:
                    pass 
            teams.append(row_data)
    except Exception as e:
        print('could not find table', e)

    teams_df = pd.DataFrame(teams, columns=team_headers)
    
    try:
        date_dropdown = driver.find_element(By.XPATH, '/html/body/header/section/p/select[2]')
        select = Select(date_dropdown)
        date = select.first_selected_option.text.strip()
        teams_df['Date'] = date
    except Exception as e:
        print('couldnt save date', e)

    return teams_df, hrefs, date

def extract_teams():
    driver = set_up_driver()
    go_to_page('https://sofifa.com/teams?type=all&lg%5B0%5D=39&showCol%5B%5D=ti&showCol%5B%5D=fm&showCol%5B%5D=oa&showCol%5B%5D=at&showCol%5B%5D=md&showCol%5B%5D=df&showCol%5B%5D=cw&showCol%5B%5D=ps', driver)
    df, hrefs, date = extact_teams_and_href(driver)
    
    return df, hrefs, date


df, hrefs, date = extract_teams()

df.to_csv(f'data/scraping/teams_{date}', index=False)
with open('hrefs.txt', 'w') as f:
    for href in hrefs:
        f.write(href + '\n')
        

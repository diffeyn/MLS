import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import math
import utils as utils

def set_up_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--force-device-scale-factor=1")

    # Look human
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )



    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
    })
    
    return driver

###--------------EXTRACT MATCH LINKS----------------###
def extract_match_links(driver, url):
    wait = WebDriverWait(driver, 10)
    
    ### Load the page
    driver.get(url)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "body")))

    ### Dismiss cookie popup if present
    utils.dismiss_cookies(driver)
    

    ### find last week's matches
    all_links = set()


    try:
        previous_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Previous results']"))) # Locate the "Previous results" button

        previous_button.click() # Click the button to get to last week's matches

        time.sleep(5)
        
        matches_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'mls-c-schedule__matches')))
        if not matches_table:
            print("No matches table found on this page.")
            
        ### Extract all match links    
        hrefs = matches_table.find_elements(By.TAG_NAME, 'a')
        
        for href in hrefs:
            all_links.add(href.get_attribute('href'))
            
    except Exception as e:
        print(f"Error occurred: {e}")
            
    return list(all_links)

def create_match_id(link):
    if link is None or (isinstance(link, float) and math.isnan(link)) or str(link).strip() == '' or str(link).strip().lower() == 'nan':
        return None
    return link.rstrip('/').split('/')[-1].split('?')[0]


def extract_feed(driver, link, match_id):
    wait = WebDriverWait(driver, 5)
    driver.get(link)
    feed = []
    
    try:
        feed_button = driver.find_element(By.XPATH,
                            "//*[normalize-space(text())='Feed']")

        feed_button.click()
        
        utils.js_scroll_by(driver, 900)

        utils.js_scroll_by(driver, 3000)
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[normalize-space(text())='First half begins.']")))

        first_half = driver.find_element(By.XPATH, "//*[normalize-space(text())='First half begins.']")

        utils.js_scroll_into_view(driver, first_half)
        if not first_half:
            print(f"First half element not found for link {link}")
        try:            
            cont = driver.find_element(By.CSS_SELECTOR, 'div[class="mls-o-match-feed"]')

            events = cont.find_elements(By.CSS_SELECTOR, 'div[class="mls-o-match-feed__container"]')

            for event in events:
                minute_el = event.find_elements(By.CSS_SELECTOR, ".mls-o-match-summary__regular-time")
                minute = minute_el[0].text.strip() if minute_el else None

                title_el = event.find_elements(By.CSS_SELECTOR, ".mls-o-match-feed__title")
                title = title_el[0].text.strip() if title_el else None

                comment_el = event.find_elements(By.CSS_SELECTOR, ".mls-o-match-feed__comment")
                comment = comment_el[0].text.strip() if comment_el else None
                
                players_wrap = event.find_elements(By.XPATH, ".//*[contains(@class,'mls-o-match-feed__players')]")

                out_player = None
                in_player = None

                if players_wrap:
                    out_nodes = players_wrap[0].find_elements(
                        By.CSS_SELECTOR, ".mls-o-match-feed__sub-out .mls-o-match-feed__player"
                    )
                    in_nodes = players_wrap[0].find_elements(
                        By.CSS_SELECTOR, ".mls-o-match-feed__sub-in .mls-o-match-feed__player"
                    )

                    out_player = out_nodes[0].text.strip() if out_nodes and out_nodes[0].text.strip() else None
                    in_player  = in_nodes[0].text.strip()  if in_nodes and in_nodes[0].text.strip()  else None
                else:
                    pass

                feed.append({
                    'match_id': match_id,
                    'minute': minute,
                    'title': title,
                    'comment': comment,
                    'out_player': out_player,
                    'in_player': in_player
                })
                if not feed:
                    print(f"No feed events found for link {link}")
        except Exception as e:
            print(f"Error extracting feed events for link {link}: {e}")
    except Exception as e:
        print(f"Error extracting feed for link {link}: {e}")
    return feed


def extract_stats(driver, link, match_id):
    wait = WebDriverWait(driver, 10)
    
    driver.get(link)
    
    general_stats = []
    shooting_stats = []
    passing_stats = []
    possession_stats = []
    xg_stats = []
    
    main_body = driver.find_element(By.TAG_NAME, 'main')
    stats_bttn = main_body.find_element(By.LINK_TEXT, 'Stats')

    try:
        stats_bttn.click()

        try:
            general_cont = wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//section[contains(@class,"mls-l-module--stats-comparison")'
                    ' and contains(@class,"mls-l-module--general")'
                    ' and not(contains(@style,"display: none"))]')))


            utils.js_scroll_into_view(driver, general_cont)
            general_cards = utils.scrape_cards(general_cont, driver)

            for it in general_cards:
                general_stats.append({
                    'stat_name': it['stat'],
                    'home_value': it['first'],
                    'away_value': it['second']
                })
        except Exception as e:
            print(f"Error occurred while scraping general stats: {e}")

        try:
            clubs_wrap = wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    '//section[contains(@class,"d3-l-section-row")][@data-toggle="clubs" and not(contains(@style,"display: none"))]'
                )))

            shooting_cont = clubs_wrap.find_element(
                By.XPATH,
                './/section[contains(@class,"mls-l-module--shooting-breakdown")]'
            )

            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                shooting_cont)

            shooting_cards = utils.scrape_cards(shooting_cont, driver)

            for it in shooting_cards:
                shooting_stats.append({
                    'stat_name': it['stat'],
                    'home_value': it['first'],
                    'away_value': it['second']
                })

        except Exception as e:
            print(f"Error occurred while scraping shooting stats: {e}")

        try:
            passing_cont = driver.find_element(By.XPATH, '//section[contains(@class,"passing-breakdown")]')

            passing_cards = utils.scrape_cards(passing_cont, driver)
            for it in passing_cards:
                passing_stats.append({
                    'stat_name': it['stat'],
                    'home_value': it['first'],
                    'away_value': it['second']
                })

        except Exception as e:
            print(f"Error occurred while scraping passing stats: {e}")

        try:
            possession_cont = driver.find_element(By.XPATH, '//section[contains(@class,"--possession")]')
            bar_cont = possession_cont.find_element(By.XPATH, './/*[contains(@class,"mls-o-possession__intervals")]')

            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                bar_cont)


            for bar in bar_cont.find_elements(By.XPATH, './/div[contains(@class,"mls-o-possession__average-intervals")]'):
                tip_id = bar.get_attribute('data-for')

                tooltips = bar.find_elements(By.XPATH, './/div[contains(@class,"__react_component_tooltip")]')

                tip = wait.until(EC.presence_of_element_located((By.ID, tip_id)))

                spans = tip.find_elements(By.XPATH, './/span')

                texts = [s.get_attribute('textContent').strip() for s in spans]
                texts = [t for t in texts if t and t.upper() != 'SKIP TO MAIN CONTENT']

                if len(texts) >= 4:
                    home_poss, home_adv, away_poss, away_adv = texts[:4]
                else:
                    home_poss = home_adv = away_poss = away_adv = None

                possession_stats.append({
                    'tip_id': tip_id,
                    'home_possession': home_poss,
                    'home_advantage': home_adv,
                    'away_possession': away_poss,
                    'away_advantage': away_adv
                })
        except Exception as e:
            print(f"Error occurred while scraping possession stats: {e}")

        try:
            xg_mod_xpath = (
                '//section[@data-toggle="clubs" and not(contains(@style,"display: none"))]'
                '//section[contains(@class,"mls-l-module--expected-goals")]'
            )
            xg_mod = wait.until(EC.visibility_of_element_located((By.XPATH, xg_mod_xpath)))

            groups = xg_mod.find_elements(
                By.CSS_SELECTOR,
                '.mls-o-expected-goals__chart-group, .mls-o-expected-goals__club-group'
            )
            chart_group = next(
                (g for g in groups if 'mls-o-expected-goals__chart-group' in (g.get_attribute('class') or '')),
                None
            )
            if chart_group is None:
                raise Exception("xG chart-group not found")

            # ensure cards exist
            wait.until(lambda d: any(
                e.is_displayed() for e in chart_group.find_elements(By.CSS_SELECTOR, '.mls-o-stat-chart')
            ))

            for card in chart_group.find_elements(By.CSS_SELECTOR, '.mls-o-stat-chart'):
                header = card.find_element(By.CSS_SELECTOR,  '.mls-o-stat-chart__header')
                first  = card.find_element(By.CSS_SELECTOR,  '.mls-o-stat-chart__first-value')
                second = card.find_element(By.CSS_SELECTOR,  '.mls-o-stat-chart__second-value')

                stat_name  = (header.text or header.get_attribute('textContent') or '').strip()
                home_value = (first.text  or first.get_attribute('textContent')  or '').strip()
                away_value = (second.text or second.get_attribute('textContent') or '').strip()

                xg_stats.append({
                    'stat_name': stat_name,
                    'home_value': home_value,
                    'away_value': away_value
                })
        except Exception as e:
            print(f"Error occurred while scraping expected goals stats: {e}")

    except Exception as e:
        print(f"Error occurred while scraping stats: {e}")
        pass

    player_rows = []
    gk_rows = []

    try:
        utils.js_scroll_by(driver, -3000)

        player_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.mls-o-buttons__segment[value="players"]')))
        player_btn.click()


        players_mod = wait.until(EC.visibility_of_element_located((
            By.XPATH,
            '//section[contains(@class,"mls-l-module--match-hub-player-stats") and not(contains(@style,"display: none"))]'
        )))

        utils.js_scroll_into_view(driver, players_mod)

        club_blocks = players_mod.find_elements(By.CSS_SELECTOR, '.mls-c-stats--match-hub-player-stats')

        for idx, block in enumerate(club_blocks):
            side = 'home' if idx == 0 else 'away'
            club_abbrev_el = block.find_elements(By.CSS_SELECTOR, '.mls-c-stats__club-abbreviation')
            club_abbrev = club_abbrev_el[0].text.strip() if club_abbrev_el else None

            for tbl in block.find_elements(By.CSS_SELECTOR, 'table.mls-o-table'):
                cls = (tbl.get_attribute('class') or '').lower()
                is_gk = 'goalkeeper' in cls

                header_cells = tbl.find_elements(
                    By.CSS_SELECTOR,
                    'thead .mls-o-table__header-group:not(.mls-o-table__header-group--main) .mls-o-table__header'
                )
                if not header_cells:
                    header_cells = tbl.find_elements(By.CSS_SELECTOR, 'thead .mls-o-table__header')

                headers = [(h.text or h.get_attribute('textContent') or '').strip() for h in header_cells]

                for tr in tbl.find_elements(By.CSS_SELECTOR, 'tbody .mls-o-table__row'):
                    cells = tr.find_elements(By.CSS_SELECTOR, '.mls-o-table__cell')
                    values = [(c.text or c.get_attribute('textContent') or '').strip() for c in cells]

                    if len(values) < len(headers):
                        values += [''] * (len(headers) - len(values))
                    elif len(values) > len(headers):
                        values = values[:len(headers)]

                    row = dict(zip(headers, values))
                    row.update({
                        'match_id': match_id,
                        'side': side,
                        'club': club_abbrev
                    })

                    if is_gk:
                        gk_rows.append(row)
                    else:
                        player_rows.append(row)

                    combined_rows = player_rows + gk_rows

    except Exception as e:
        print(f"Error occurred while scraping player stats: {e}")
        
    general_stats_df = pd.DataFrame(general_stats);  general_stats_df["category"] = "general"
    shooting_stats_df = pd.DataFrame(shooting_stats); shooting_stats_df["category"] = "shooting"
    passing_stats_df = pd.DataFrame(passing_stats);   passing_stats_df["category"] = "passing"
    possession_stats_df = pd.DataFrame(possession_stats); possession_stats_df["category"] = "possession"
    expected_goals_stats_df = pd.DataFrame(xg_stats); expected_goals_stats_df["category"] = "xg"
    player_stats_df = pd.DataFrame(combined_rows)

    all_stats = pd.concat(
        [general_stats_df, shooting_stats_df, passing_stats_df, possession_stats_df, expected_goals_stats_df],
        axis=0, ignore_index=True
    )

    player_stats_df['match_id'] = match_id
    all_stats['match_id'] = match_id
    return all_stats, player_stats_df

def add_match_id(obj, match_id):
    if obj is None:
        df = pd.DataFrame()
    elif isinstance(obj, pd.DataFrame):
        df = obj.copy()
    else:
        df = pd.DataFrame(obj)

    if df.empty:
        return pd.DataFrame({'match_id': [match_id]})

    if 'match_id' not in df.columns:
        df.insert(0, 'match_id', match_id)

    return df


def extract_match_data(links, driver):

    latest_stats = []
    latest_player_stats = []
    latest_feed = []

    for link in links:
        if (link is None or (isinstance(link, float) and math.isnan(link))
                or str(link).strip() == '' or str(link).strip().lower() == 'nan'):
            print(f"[skip] bad link: {link!r}")
            continue

        match_id = link.rstrip('/').split('/')[-1].split('?')[0]

        feed = extract_feed(driver, link, match_id)
        feed = add_match_id(feed, match_id)

        stats, player_stats = extract_stats(driver, link, match_id)
        stats = add_match_id(stats, match_id)
        player_stats = add_match_id(player_stats, match_id)

        latest_stats.append(stats)
        latest_player_stats.append(player_stats)
        latest_feed.append(feed)

        latest_stats_df = pd.concat(latest_stats, axis=0, ignore_index=True) if latest_stats else pd.DataFrame(columns=['match_id'])
        latest_player_stats_df = pd.concat(latest_player_stats, axis=0, ignore_index=True) if latest_player_stats else pd.DataFrame(columns=['match_id'])
        latest_feed_df = pd.concat(latest_feed, axis=0, ignore_index=True) if latest_feed else pd.DataFrame(columns=['match_id'])
    driver.quit()

    return latest_stats_df, latest_player_stats_df, latest_feed_df




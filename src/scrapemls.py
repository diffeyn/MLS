#!/usr/bin/env python3

import bs_scraper as bscraper
import selenium_scraper as sscraper
import utils as utils
import datetime

sofifa_url = 'https://sofifa.com/teams?type=all&lg%5B%5D=39'

def scrape_sofifa(sofifa_url):
    soup = bscraper.get_soup(sofifa_url)
    teams_df, team_links = bscraper.scrape_team_table(soup)
    players_df = bscraper.extract_players(team_links)
    return teams_df, players_df

mls_url = 'https://www.mlssoccer.com/schedule/scores#competition=MLS-COM-000001&club=all'

def scrape_mls(mls_url):
    driver = sscraper.set_up_driver()
    links = sscraper.extract_match_links(driver, mls_url)
    latest_stats, latest_player_stats, latest_feed = sscraper.extract_match_data(links, driver)
    
    return latest_stats, latest_player_stats, latest_feed


latest_teams, latest_players = scrape_sofifa(sofifa_url)
latest_stats, latest_player_stats, latest_feed = scrape_mls(mls_url)

today = datetime.date.today()

utils.save_to_csv(latest_teams, f'teams/latest_teams_{today}.csv')
utils.save_to_csv(latest_players, f'players/latest_players_{today}.csv')
utils.save_to_csv(latest_stats, f'stats/latest_stats_{today}.csv')
utils.save_to_csv(latest_player_stats, f'player_stats/latest_player_stats_{today}.csv')
utils.save_to_csv(latest_feed, f'feed/latest_feed_{today}.csv')

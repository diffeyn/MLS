#!/usr/bin/env python3

import bs_scraper as bscraper
import selenium_scraper as sscraper
import utils as utils

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


utils.save_to_csv(latest_teams, 'latest_teams.csv')
utils.save_to_csv(latest_players, 'latest_players.csv')
utils.save_to_csv(latest_stats, 'latest_stats.csv')
utils.save_to_csv(latest_player_stats, 'latest_player_stats.csv')
utils.save_to_csv(latest_feed, 'latest_feed.csv')

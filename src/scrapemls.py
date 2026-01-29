#!/usr/bin/env python3

import bs_scraper as bscraper
import selenium_scraper as sscraper
import utils as utils
import datetime
import cleaning
import pandas as pd


sofifa_url = 'https://sofifa.com/teams?type=all&lg%5B%5D=39'

def scrape_sofifa(sofifa_url):
    soup = bscraper.get_soup(sofifa_url)
    sofifa_teams_df, team_links = bscraper.scrape_team_table(soup)

    sofifa_players_df = bscraper.extract_players(team_links)

    return sofifa_teams_df, sofifa_players_df

mls_url = 'https://www.mlssoccer.com/schedule/scores#competition=MLS-COM-000001&club=all'

def scrape_mls(mls_url):
    driver = sscraper.set_up_driver()
    links = sscraper.extract_match_links(driver, mls_url)
    mls_latest_team_stats, mls_latest_player_stats, mls_latest_feed = sscraper.extract_match_data(links, driver)

    return mls_latest_team_stats, mls_latest_player_stats, mls_latest_feed


sofifa_teams_df, sofifa_players_df = scrape_sofifa(sofifa_url)
mls_latest_team_stats, mls_latest_player_stats, mls_latest_feed = scrape_mls(mls_url)

today = datetime.date.today()

sofifa_players_df = cleaning.clean_player_stats(sofifa_players_df)
sofifa_teams_df = cleaning.clean_teams(sofifa_teams_df)
mls_latest_feed = cleaning.clean_feed(mls_latest_feed)
mls_latest_team_stats = cleaning.clean_teams_stats(mls_latest_team_stats)
mls_latest_team_stats = cleaning.reframe_stats(mls_latest_team_stats)
mls_latest_player_stats = cleaning.clean_players(mls_latest_player_stats)

mls_simple_matches = cleaning.simple_matches(mls_latest_player_stats)



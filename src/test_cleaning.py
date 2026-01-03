import pandas as pd
import cleaning

df = pd.read_csv("data/scraping/matches/feed/feed_atlvscin-05-25-2025.csv")
print(cleaning.clean_player_stats(df).head())
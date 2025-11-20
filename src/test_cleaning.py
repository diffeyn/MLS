import pandas as pd
from cleaning.clean_feed import clean_feed


df = pd.read_csv("data/scraping/matches/raw/feed/any_feed_file.csv")
print(clean_feed(df).head())
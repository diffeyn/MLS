import pandas as pd

def clean_players(df):
    df = df.rename(columns={
        'match_id': 'match_id',
        'Player': 'player_name',
        'Mins': 'minutes',
        'G' : 'goals',
        'xG': 'expected_goals',
        'Conv%' : 'shot_conv_perc',
        'SOT' : 'on_target',
        'Pass%' : 'pass_perc',
        'A' : 'assists',
        'P' : 'passes',
        'Cross' : 'cross',
        'CK' : 'corner_kick',
        'KP' : 'key_pass',
        'AD' : 'aerial',
        'AD%' : 'aerial_perc',
        'FC' : 'fouls',
        'FS' : 'fouls_against',
        'OFF' : 'offside',
        'YC' : 'yellow_card',
        'RC' : 'red_card'
    })
    
    if 'match_id' in df.columns:
        df = df[['match_id'] + [c for c in df.columns if c != 'match_id']]
    else:
        print("No match_id column found. Columns are:", df.columns.tolist())    
    
    return df

import pandas as pd

def clean_players(df):
    """
    Clean and standardize player statistics data from MLS matches.
    This function renames columns from their abbreviated forms to more descriptive names
    and ensures that 'match_id' is the first column in the resulting DataFrame.
    Parameters
    ----------
    df : pandas.DataFrame
        A DataFrame containing player statistics with columns in their original/abbreviated form.
        Expected to contain columns like 'Player', 'Mins', 'G', 'xG', etc.
    Returns
    -------
    pandas.DataFrame
        A cleaned DataFrame with standardized column names and 'match_id' as the first column.
        Column mappings include:
        - Player -> player_name
        - Mins -> minutes
        - G -> goals
        - xG -> expected_goals
        - Conv% -> shot_conv_perc
        - SOT -> on_target
        - Pass% -> pass_perc
        - A -> assists
        - P -> passes
        - Cross -> cross
        - CK -> corner_kick
        - KP -> key_pass
        - AD -> aerial
        - AD% -> aerial_perc
        - FC -> fouls
        - FS -> fouls_against
        - OFF -> offside
        - YC -> yellow_card
        - RC -> red_card
    Notes
    -----
    If 'match_id' column is not found in the input DataFrame, a warning message
    will be printed to the console listing all available columns.
    """
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

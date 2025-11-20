import pandas as pd
import re
def reframe_stats(df, fname: str | None = None):
    if fname is None:
        fname = str(df.attrs.get('source_filename', '') or '')

    df = df.copy()
    m = re.search(r'([a-z]{3})[ _-]*v?s[ _-]*([a-z]{3}).*?(\d{2}-\d{2}-\d{4})', fname, re.I)

    parts = []
    if m:
        home, away, date_str = m.groups()
        home, away = home.upper(), away.upper()
        date = pd.to_datetime(date_str, format="%m-%d-%Y")
        parts.append(pd.DataFrame({'home_value': [home], 'away_value': [away], 'stat': ['teams']}))
        parts.append(pd.DataFrame({'home_value': [date], 'away_value': [date], 'stat': ['date']}))

    if parts:
        df = pd.concat([df, *parts], ignore_index=True)

    need = {'stat', 'home_value', 'away_value'}
    missing = need - set(df.columns)
    if missing:
        raise KeyError(f"reframe_stats expected {need}; missing {missing}. Got: {list(df.columns)[:10]}")

    out = {}
    for _, row in df.iterrows():
        out[f"{row['stat']}_home"] = row['home_value']
        out[f"{row['stat']}_away"] = row['away_value']

    wide = pd.DataFrame([out])
    if 'date_away' in wide.columns:
        wide = wide.drop(columns=['date_away'])
    wide = wide.rename(columns={'date_home': 'match_date'})
    wide.columns = (pd.Index(wide.columns)
                    .str.replace(' ', '_')
                    .str.replace('%', 'pct')
                    .str.replace('-', '_')
                    .str.lower())
    
    if 'match_id' in df.columns:                
        wide.insert(0, 'match_id', df['match_id'].iloc[0])  
        
    return wide

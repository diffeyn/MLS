import pandas as pd
import re 
import hashlib
from pathlib import Path
from datetime import datetime
import hashlib

##3 clean feed

def clean_feed(df):
    df = df.copy()

    df = df.dropna(subset=['minute', 'title', 'comment'], how='all')
    
    df['title'] = df.apply(lambda x: 'Corner' if pd.notna(x['comment']) and 'corner' in x['comment'].lower() else x['title'], axis=1)

    df['title'] = df.apply(lambda x: 'Foul' if pd.notna(x['comment']) and 'foul' in x['comment'].lower() else x['title'], axis=1)

    df['title'] = df.apply(lambda x: 'Offside' if pd.notna(x['comment']) and 'offside' in x['comment'].lower() else x['title'], axis=1)   
    
    df = df[~df['comment'].str.contains('Lineups', na=False)]

    df = df[~df['title'].str.contains('KICK OFF|HALF TIME|FULL TIME|END OF SECOND HALF', na=False)]
    
    df = df[df['minute'].notna()]
    
    df = df.iloc[::-1].reset_index(drop=True)
    
    return df

### clean match player data

def clean_players(df):
    df = df.rename(columns={
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
    
    df = df[['match_id'] + [col for col in df.columns if col != 'match_id']]
    
    return df

### clean match team data

def clean_teams(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.iloc[:, 1:-1]

    rename_map = {
        "Name": "team_name",
        "ID": "team_id",
        "Formation": "team_formation",
        "Overall": "overall_score",
        "Attack": "attack",
        "Midfield": "midfield",
        "Defence": "defense",
        "Players": "num_players",
    }

    for possible in ["Club worth", "Club.worth"]:
        if possible in df.columns:
            rename_map[possible] = "worth_euro"

    df = df.rename(columns=rename_map)

    if "team_formation" in df.columns:
        split_cols = df["team_formation"].str.split(" ", expand=True)
        if split_cols.shape[1] >= 2:
            df["lineup"] = split_cols[0]
            df["style"] = split_cols[1]
        if split_cols.shape[1] >= 3:
            df["trash2"] = split_cols[2]
        else:
            df["trash2"] = None

    df["team_name"] = df["team_name"].str.replace("Major League Soccer", "", regex=False)

    if "worth_euro" in df.columns:
        df["worth_euro"] = (
            df["worth_euro"]
            .astype(str)
            .str.replace("€", "", regex=False)
            .str.replace("M", "", regex=False)
        )

    numeric_cols = ["overall_score", "attack", "midfield", "defense", "worth_euro", "num_players"]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "trash2" in df.columns:
        df = df.drop(columns=["trash2"])

    if "team_id" in df.columns:
        df = df.set_index("team_id")

    return df


def safe_eval(x):
    try:
        if '+' in str(x):
            return sum(int(i) for i in str(x).split('+'))
        elif '-' in str(x):
            return int(str(x).split('-')[0]) - sum(int(i) for i in str(x).split('-')[1:])
        else:
            return int(x)
    except:
        return x

def clean_player_stats(df):
    df = df.copy()

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    df.loc[:, 'Name'] = df['Name'].str.replace(r'[A-Z]+$', '', regex=True)
    df.loc[:, 'date'] = pd.to_datetime(df['date']).dt.date

    pat = r'(\w+)\((\d+)\)(\d{4}) ~ (\d{4})'
    df[['position', 'jersey_num', 'contract_start',
        'contract_end']] = df.loc[:, 'Team & Contract'].astype(str).str.extract(pat)

    df.loc[:, 'height_cm'] = df['Height'].astype(str).str.split('cm / ').str[0].astype('Int64')
    df.loc[:, 'weight_kg'] = df['Weight'].astype(str).str.split('kg / ').str[0].astype('Int64')

    df.loc[:, 'wage_eur'] = df['Wage'].astype(str).str.replace('€', '').str.replace(
        ',', '').str.replace('K', '000').str.replace('M',
                                                     '000000').astype('Int64')

    df.loc[:, 'value_eur'] = df['Value'].astype(str).str.replace('€', '').str.replace(
        ',', '').str.replace('.', '').str.replace('K', '000').str.replace(
            'M', '000000').astype('Int64')


    df.drop(columns=['Height', 'Weight', 'Team & Contract', 'Value', 'Wage'],
            inplace=True)
    
    ## safe eval everything but date
    for col in df.columns:
        if col != 'date':
            df[col] = df[col].apply(safe_eval)

    
    main_cols = [
        'ID', 'date', 'Name', 'Age', 'height_cm', 'weight_kg', 'team',
        'contract_start', 'contract_end', 'position', 'foot', 'jersey_num',
        'wage_eur', 'value_eur'
    ]

    rest_cols = [col for col in df.columns if col not in main_cols]
    df = df[main_cols + rest_cols]

    for c in df.columns:
        try:
            df[c] = pd.to_numeric(df[c])
        except (ValueError, TypeError):
            pass 

    df.columns = df.columns.str.lower().str.replace(' ', '_')

    return df


### clean match stats data

def clean_teams_stats(df):
    bar_dict = {
        '0-5': 'bar_0',
        '6-10': 'bar_1',
        '11-15': 'bar_2',
        '16-20': 'bar_3',
        '21-25': 'bar_4',
        '26-30': 'bar_5',
        '31-35': 'bar_6',
        '36-40': 'bar_7',
        '41-45': 'bar_8',
        '46-50': 'bar_2_0',
        '51-55': 'bar_2_1',
        '56-60': 'bar_2_2',
        '61-65': 'bar_2_3',
        '66-70': 'bar_2_4',
        '71-75': 'bar_2_5',
        '76-80': 'bar_2_6',
        '81-85': 'bar_2_7',
        '86-90': 'bar_2_8',
    }

    bar_dict_switched = {v: k for k, v in bar_dict.items()}
    df = df.copy()
    df = df.drop(columns=['home_advantage', 'away_advantage'])
    df['stat'] = df['category'].astype(str) + '_' + df['stat_name'].astype(str)
    df = df.drop(columns=['category', 'stat_name'])
    df['tip_id'] = df['tip_id'].astype(str).str.strip() 
    df['tip_id'] = df['tip_id'].replace(bar_dict_switched)
    mask = df["tip_id"].astype(str).str.match(r"^\d{1,2}-\d{1,2}$", na=False)
    h_pct = df.loc[mask, "home_possession"].astype(str).str.extract(r"(\d+(?:\.\d+)?)")[0].astype(float)
    a_pct = df.loc[mask, "away_possession"].astype(str).str.extract(r"(\d+(?:\.\d+)?)")[0].astype(float)
    df.loc[mask, "home_value"] = h_pct.values 
    df.loc[mask, "away_value"] = a_pct.values
    df.loc[mask, "stat"] = "possession_" + df.loc[mask, "tip_id"].str.replace("-", "_", regex=False)
    df = df.drop(columns=['tip_id', 'home_possession', 'away_possession'])
    df = df[['stat', 'home_value', 'away_value']]
    return df


### reframe stats

def reframe_stats(df):
    fname = df.attrs.get('source_filename', '')

    # regex: match 'cleaned_stats_' + home + 'vs' + away + '-' + date + '.csv'
    m = re.match(r"cleaned_stats_([a-z]{2,4})vs([a-z]{2,4})-(\d{2}-\d{2}-\d{4})\.csv", fname, re.I)

    if m:
        home, away, date_str = m.groups()
        home, away = home.upper(), away.upper()
        date = pd.to_datetime(date_str, format="%m-%d-%Y")

        # add rows with stat = date and team = teams
        add_df = pd.DataFrame({
            'home_value': [home],
            'away_value': [away],
            'stat': 'teams'
        })
        
        new_row = pd.DataFrame({
            'home_value': [date],
            'away_value': [date],
            'stat': 'date'
        })

    df = pd.concat([df, add_df], ignore_index=True)

    df = pd.concat([df, new_row], ignore_index=True)
    out = {}
    for _, row in df.iterrows():
        out[f"{row['stat']}_home"] = row['home_value']
        out[f"{row['stat']}_away"] = row['away_value']

    wide = pd.DataFrame([out])
    wide= wide.drop(columns=['date_home'])
    wide['match_date'] = wide['date_away']
    wide = wide.drop(columns=['date_away'])
    wide.columns = [c.replace(' ', '_').replace('%', 'pct').replace('-', '_').lower() for c in wide.columns]
    return wide



TYPE_PREFIXES = ("player_stats_", "simple_stats_", "players_", "stats_", "feed_", "reframed_stats_")

MLS_CODES = {
    "atl","chi","cin","clb","col","dal","dcu","hou","kcw","lag","laf","mcf","mia","min","mon","nsh",
    "ner","nyc","nyr","orl","phi","por","rsl","sea","sje","stl","tor","van","aus","cha"
}

def _strip_cleaned_and_prefixes(stem: str) -> tuple[str, str]:
    s = stem.lower()
    if s.startswith("cleaned_"):
        s = s[len("cleaned_"):]
    detected = None
    for pref in TYPE_PREFIXES:
        if s.startswith(pref):
            detected = pref.rstrip("_")
            s = s[len(pref):]
            break
    return detected or "unknown", s

def _extract_date_chunk(name: str) -> tuple[str, str]:
    for pat in [r"(\d{4})[^\d]?(\d{1,2})[^\d]?(\d{1,2})",   # YYYY-MM-DD
                r"(\d{1,2})[^\d]?(\d{1,2})[^\d]?(\d{4})"]:  # MM-DD-YYYY
        m = re.search(pat, name)
        if not m:
            continue
        g = tuple(int(x) for x in m.groups())
        try:
            if len(str(g[0])) == 4:
                dt = datetime(g[0], g[1], g[2])
            else:
                dt = datetime(g[2], g[0], g[1])
            yyyymmdd = dt.strftime("%Y%m%d")
            remainder = name[:m.start()] + name[m.end():]
            return yyyymmdd, remainder
        except ValueError:
            pass
    return "00000000", name

def _extract_teams(remainder: str) -> tuple[str, str]:

    m = re.search(r"([a-z]{3})[ _\-]*v?s?[ _\-]*([a-z]{3})", remainder)
    if m:
        t1, t2 = m.group(1), m.group(2)
        return t1, t2

    letters = re.sub(r"[^a-z]", "", remainder)
    if len(letters) >= 6:
        t1, t2 = letters[:3], letters[3:6]
        if MLS_CODES and (t1 not in MLS_CODES or t2 not in MLS_CODES):
            found = [letters[i:i+3] for i in range(0, len(letters)-2, 3)]
            valid = [c for c in found if c in MLS_CODES]
            if len(valid) >= 2:
                return valid[0], valid[1]
        return t1, t2

    return "unk", "unk"

def canonical_key_from_stem(stem: str) -> tuple[str, str, str, str]:
    dtype, remainder = _strip_cleaned_and_prefixes(stem)
    yyyymmdd, leftover = _extract_date_chunk(remainder)
    home, away = _extract_teams(leftover)
    return dtype, home, away, yyyymmdd

def make_match_id(key: str, length: int = 10) -> str:
    return "match_" + hashlib.md5(key.encode("utf-8")).hexdigest()[:length]

def attach_match_id(df: pd.DataFrame, file_path: Path) -> tuple[pd.DataFrame, str, str, str]:
    stem = file_path.stem
    dtype, home, away, yyyymmdd = canonical_key_from_stem(stem)
    canonical_key = f"{home}_{away}_{yyyymmdd}"
    match_id = make_match_id(canonical_key)
    out = df.copy()
    out["canonical_key"] = canonical_key
    out["match_id"] = match_id
    return out, dtype, canonical_key, match_id

def save_with_match_id(df: pd.DataFrame, dtype: str, match_id: str, repo_root: Path) -> Path:

    out_dir = repo_root / "data" / "clean" / "w_match_id" / dtype
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"cleaned_{dtype}_{match_id}.csv"
    df.to_csv(out_path, index=False)
    print(f"✔ wrote {out_path}  rows={len(df)}")
    return out_path

def replace_match_id_with_hash(df: pd.DataFrame, col: str = "match_id") -> pd.DataFrame:
    out = df.copy()

    def make_hash(val: str) -> str:
        if not isinstance(val, str) or not val:
            return "match_00000000"
        val = re.sub(r"[^a-z0-9]", "", val.lower())
        return "match_" + hashlib.md5(val.encode("utf-8")).hexdigest()[:8]

    out["match_id_hash"] = out[col].apply(make_hash)
    out = out.drop(columns=[col])
    return out

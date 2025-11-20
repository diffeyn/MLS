import hashlib
import pandas as pd

def hash_match_ids(df: pd.DataFrame, col="match_id", out_col="match_id_hash", length=8):
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found.")
    
    df = df.copy()
    df[out_col] = (
        df[col]
        .astype(str)
        .str.lower()
        .map(lambda x: hashlib.md5(x.encode()).hexdigest()[:length])
    )
    
    df = df.drop(columns=[col], errors='ignore')
    
    return df
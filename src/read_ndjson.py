import pandas as pd

def read_ndjson(filepath):
    df = pd.read_json(filepath, lines=True)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


import pandas as pd

def next_id(df: pd.DataFrame, id_col: str = "id") -> int:
    if df.empty:
        return 1
    try:
        return int(df[id_col].max()) + 1
    except Exception:
        return 1

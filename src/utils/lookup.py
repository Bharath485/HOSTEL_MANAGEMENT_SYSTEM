from typing import Dict
import pandas as pd

def id_to_label(df: pd.DataFrame, id_col: str, label_col: str) -> Dict[int, str]:
    m: Dict[int, str] = {}
    if id_col in df and label_col in df:
        for _, row in df.iterrows():
            try:
                m[int(row[id_col])] = str(row[label_col])
            except Exception:
                continue
    return m

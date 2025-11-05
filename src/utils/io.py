
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

def ensure_csv(path: str, columns: list[str]) -> None:
    """Create the CSV with headers if it doesn't exist."""
    if not os.path.exists(path):
        df = pd.DataFrame(columns=columns)
        df.to_csv(path, index=False)

def csv_path(filename: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, filename)

def read_csv(filename: str, columns: list[str]) -> pd.DataFrame:
    path = csv_path(filename)
    ensure_csv(path, columns)
    return pd.read_csv(path)

def write_csv(filename: str, df: pd.DataFrame) -> None:
    path = csv_path(filename)
    df.to_csv(path, index=False)

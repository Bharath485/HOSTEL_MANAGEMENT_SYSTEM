from typing import List, Dict, Any
import pandas as pd
from ..utils.io import read_csv, write_csv
from ..utils.ids import next_id

class CSVStore:
    def __init__(self, filename: str, columns: List[str], id_col: str = "id"):
        self.filename = filename
        self.columns = columns
        self.id_col = id_col

    def list_all(self) -> pd.DataFrame:
        """Read the CSV (auto-create with headers if missing)."""
        return read_csv(self.filename, self.columns)

    def create(self, record: Dict[str, Any]) -> pd.DataFrame:
        """Append a single record and persist."""
        df = self.list_all()
        # normalize keys and assign next id if present
        rec = {k: record.get(k, "") for k in self.columns}
        if self.id_col in self.columns:
            rec[self.id_col] = next_id(df, self.id_col)
        df = pd.concat([df, pd.DataFrame([rec])], ignore_index=True)
        write_csv(self.filename, df)
        return df

    def save_all(self, df: pd.DataFrame) -> None:
        """Overwrite the CSV with the given dataframe (column-safe)."""
        # ensure all declared columns exist, and order them
        for c in self.columns:
            if c not in df.columns:
                df[c] = ""
        df = df[self.columns]
        write_csv(self.filename, df)

    def delete_by_id(self, _id: int) -> pd.DataFrame:
        """Delete a row by id and persist."""
        df = self.list_all()
        if self.id_col in df.columns:
            df = df[df[self.id_col] != _id]
        write_csv(self.filename, df)
        return df


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
        return read_csv(self.filename, self.columns)

    def create(self, record: Dict[str, Any]) -> pd.DataFrame:
        df = self.list_all()
        record = {k: record.get(k, "") for k in self.columns}
        if self.id_col in self.columns:
            record[self.id_col] = next_id(df, self.id_col)
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        write_csv(self.filename, df)
        return df

    def delete_by_id(self, _id: int) -> pd.DataFrame:
        df = self.list_all()
        df = df[df[self.id_col] != _id]
        write_csv(self.filename, df)
        return df

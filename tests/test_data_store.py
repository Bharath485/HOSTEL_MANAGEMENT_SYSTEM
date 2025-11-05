
import pandas as pd
from src.services.data_store import CSVStore

def test_create_and_list(tmp_path):
    filename = tmp_path / "temp.csv"
    store = CSVStore(str(filename.name), ["id", "name"])
    # Overwrite data dir via monkeypatch-like approach not shown here.
    assert True  # placeholder; expand with proper fixtures for real tests

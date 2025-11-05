
from .data_store import CSVStore

FEE_COLUMNS = ["id", "student_id", "month", "amount", "paid_on", "status"]

fees_store = CSVStore("fees.csv", FEE_COLUMNS, id_col="id")

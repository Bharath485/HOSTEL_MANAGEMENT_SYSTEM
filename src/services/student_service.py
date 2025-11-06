
from .data_store import CSVStore

STUDENT_COLUMNS = ["id", "owner_id","name", "email", "phone", "gender", "course"]

students_store = CSVStore("students.csv", STUDENT_COLUMNS, id_col="id")

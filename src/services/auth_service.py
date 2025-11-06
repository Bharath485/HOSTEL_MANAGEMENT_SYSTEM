from .data_store import CSVStore

USER_COLUMNS = ["id", "owner_id","name", "email", "password"]

users_store = CSVStore("users.csv", USER_COLUMNS, id_col="id")

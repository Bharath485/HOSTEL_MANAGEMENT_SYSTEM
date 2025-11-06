
from .data_store import CSVStore

ROOM_COLUMNS = ["id","owner_id", "room_no", "type", "capacity", "occupied"]

rooms_store = CSVStore("rooms.csv", ROOM_COLUMNS, id_col="id")

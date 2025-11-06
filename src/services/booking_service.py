from .data_store import CSVStore
BOOKING_COLUMNS = ["id", "owner_id", "student_id", "room_id", "start_date", "end_date", "status"]
bookings_store = CSVStore("bookings.csv", BOOKING_COLUMNS, id_col="id")

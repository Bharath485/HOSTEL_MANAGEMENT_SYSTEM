from ..services.room_service import rooms_store
import pandas as pd

TYPE_CAPACITY = {"Triple": 3, "Double": 2}

def generate_default_rooms():
    """Creates 100 rooms: 01–50 Triple, 51–100 Double, if rooms.csv is empty."""
    df = rooms_store.list_all()
    if not df.empty:
        return False  # already have rooms

    rows = []
    # 01–50 Triple
    for i in range(1, 51):
        room_no = f"{i:02d}"
        rows.append({
            "id": i,
            "room_no": room_no,
            "type": "Triple",
            "capacity": TYPE_CAPACITY["Triple"],
            "occupied": 0
        })
    # 51–100 Double
    for i in range(51, 101):
        room_no = f"{i:02d}"
        rows.append({
            "id": i,
            "room_no": room_no,
            "type": "Double",
            "capacity": TYPE_CAPACITY["Double"],
            "occupied": 0
        })

    seed_df = pd.DataFrame(rows, columns=["id","room_no","type","capacity","occupied"])
    # Use rooms_store.save_all (make sure CSVStore has save_all as we added earlier)
    rooms_store.save_all(seed_df)
    return True

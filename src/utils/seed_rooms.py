from ..services.room_service import rooms_store
import pandas as pd

TYPE_CAPACITY = {"Triple": 3, "Double": 2}

def generate_default_rooms(owner_id=None) -> bool:
    """
    Create 100 rooms for a specific owner (user):
      - 01–50  -> Triple (cap 3)
      - 51–100 -> Double (cap 2)
    Returns True if created, False if this owner already has rooms.
    """
    # Load all rooms
    df = rooms_store.list_all().copy()
    # Ensure owner_id column exists even in legacy CSVs
    if "owner_id" not in df.columns:
        df["owner_id"] = None

    # If this owner already has rooms, skip
    if owner_id is not None and not df[df["owner_id"] == owner_id].empty:
        return False

    # Build rows for this owner only
    rows = []
    # 01–50 Triple
    for i in range(1, 51):
        rows.append({
            "id": None,                  # let CSVStore/save_all keep order; id not required here
            "owner_id": owner_id,
            "room_no": f"{i:02d}",
            "type": "Triple",
            "capacity": TYPE_CAPACITY["Triple"],
            "occupied": 0
        })
    # 51–100 Double
    for i in range(51, 101):
        rows.append({
            "id": None,
            "owner_id": owner_id,
            "room_no": f"{i:02d}",
            "type": "Double",
            "capacity": TYPE_CAPACITY["Double"],
            "occupied": 0
        })

    seed_df = pd.DataFrame(rows, columns=["id","owner_id","room_no","type","capacity","occupied"])

    # Append to existing data without touching other owners’ rooms
    combined = pd.concat([df, seed_df], ignore_index=True)

    # Reassign IDs sequentially if needed
    if "id" in combined.columns:
        # Fill missing ids with incremental integers
        if combined["id"].isna().any():
            # Keep existing ids; assign new ones for NaNs
            max_id = pd.to_numeric(combined["id"], errors="coerce").fillna(0).astype(int).max()
            next_id = max_id + 1
            new_ids = []
            for val in combined["id"]:
                if pd.isna(val) or str(val).strip() == "":
                    new_ids.append(next_id)
                    next_id += 1
                else:
                    new_ids.append(int(val))
            combined["id"] = new_ids
        combined["id"] = combined["id"].astype(int)

    rooms_store.save_all(combined)
    return True

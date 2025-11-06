import streamlit as st
import pandas as pd
from datetime import date, timedelta
from ..services.booking_service import bookings_store
from ..services.student_service import students_store
from ..services.room_service import rooms_store
from ..utils.lookup import id_to_label

STATUS_OPTS = ["active", "completed", "cancelled"]

# ---------- helpers: scoped merge & occupancy ----------

def _save_scoped(df_full: pd.DataFrame, df_my: pd.DataFrame, owner_id: int, store) -> None:
    """Merge only the current user's edits back into the full CSV."""
    if df_full is None:
        df_full = pd.DataFrame()
    if df_my is None:
        df_my = pd.DataFrame()

    if df_full.empty and df_my.empty:
        store.save_all(pd.DataFrame(columns=getattr(store, "columns", [])))
        return

    df_full = df_full.copy()
    df_my = df_my.copy()

    if "owner_id" not in df_full.columns:
        df_full["owner_id"] = None
    if "owner_id" not in df_my.columns:
        df_my["owner_id"] = owner_id

    others = df_full[df_full["owner_id"] != owner_id]
    merged = pd.concat([others, df_my], ignore_index=True)
    store.save_all(merged)

def _available_beds_per_room_scoped(r_my: pd.DataFrame, b_my: pd.DataFrame) -> dict[int, int]:
    """Available beds = capacity - active bookings (for this owner only). Safe with missing cols."""
    avail: dict[int, int] = {}
    if r_my is None or r_my.empty:
        return avail

    # default: no active counts
    counts: dict = {}

    if b_my is not None and not b_my.empty:
        tmp = b_my.copy()
        if "status" not in tmp.columns:
            tmp["status"] = ""
        if "room_id" not in tmp.columns:
            tmp["room_id"] = None

        tmp["status"] = tmp["status"].astype(str).str.lower()
        tmp["room_id"] = pd.to_numeric(tmp["room_id"], errors="coerce")
        tmp = tmp[(tmp["status"] == "active") & (~tmp["room_id"].isna())]

        if not tmp.empty:
            counts = tmp.groupby("room_id")["room_id"].count().astype(int).to_dict()

    for _, r in r_my.iterrows():
        rid = int(pd.to_numeric(r.get("id", 0), errors="coerce") or 0)
        cap = int(pd.to_numeric(r.get("capacity", 0), errors="coerce") or 0)
        occ = int(counts.get(rid, 0))
        avail[rid] = max(cap - occ, 0)
    return avail

def _recompute_room_occupancy_scoped(owner_id: int):
    """Recompute rooms.occupied only for this user's rooms using this user's ACTIVE bookings."""
    r_full = rooms_store.list_all().copy()
    b_full = bookings_store.list_all().copy()

    for df in (r_full, b_full):
        if "owner_id" not in df.columns:
            df["owner_id"] = None

    r_my = r_full[r_full["owner_id"] == owner_id].copy()
    b_my = b_full[b_full["owner_id"] == owner_id].copy()

    if r_my.empty:
        return

    # Ensure columns exist
    if "status" not in b_my.columns:
        b_my["status"] = ""
    if "room_id" not in b_my.columns:
        b_my["room_id"] = None

    if b_my.empty:
        r_my["occupied"] = 0
    else:
        tmp = b_my.copy()
        tmp["status"] = tmp["status"].astype(str).str.lower()
        tmp["room_id"] = pd.to_numeric(tmp["room_id"], errors="coerce")
        tmp = tmp[(tmp["status"] == "active") & (~tmp["room_id"].isna())]

        if tmp.empty:
            r_my["occupied"] = 0
        else:
            occ = tmp.groupby("room_id")["room_id"].count().rename("occ")
            r_my = r_my.merge(occ, how="left", left_on="id", right_index=True)
            r_my["occ"] = r_my["occ"].fillna(0).astype(int)
            # keep capacity numeric
            r_my["capacity"] = pd.to_numeric(r_my["capacity"], errors="coerce").fillna(0).astype(int)
            r_my["occupied"] = r_my[["occ", "capacity"]].min(axis=1)
            r_my.drop(columns=["occ"], inplace=True)

    _save_scoped(r_full, r_my, owner_id, rooms_store)

# ---------- main view ----------

def show_bookings():
    st.subheader("Bookings")

    uid = int(st.session_state["user"]["id"])

    # Load full CSVs
    s_full = students_store.list_all()
    r_full = rooms_store.list_all()
    b_full = bookings_store.list_all()

    # Ensure owner_id exists on all
    for df in (s_full, r_full, b_full):
        if "owner_id" not in df.columns:
            df["owner_id"] = None

    # Scope to current user
    s_df = s_full[s_full["owner_id"] == uid].copy()
    r_df = r_full[r_full["owner_id"] == uid].copy()
    b_df = b_full[b_full["owner_id"] == uid].copy()

    if s_df.empty or r_df.empty:
        st.info("Please add at least one Student and one Room before creating bookings.")
        st.stop()

    # Friendly maps
    student_map = id_to_label(s_df, "id", "name")
    room_map = id_to_label(r_df, "id", "room_no")

    # Availability (mine)
    avail_map = _available_beds_per_room_scoped(r_df, b_df)

    # ---------- Create booking (closed by default) ----------
    if "show_booking_form" not in st.session_state:
        st.session_state.show_booking_form = False

    if not st.session_state.show_booking_form:
        if st.button("➕ Create Booking"):
            st.session_state.show_booking_form = True
            st.rerun()
    else:
        with st.expander("New Booking", expanded=True):
            with st.form("add_booking_form", clear_on_submit=True):
                c1, c2 = st.columns(2)

                # Student selection
                student_id = c1.selectbox(
                    "Student",
                    list(student_map.keys()),
                    format_func=lambda k: f"{k} - {student_map.get(k,'')}"
                )

                # Room label shows availability: "07 (avail: 2)"
                room_choices = list(room_map.keys())
                def room_label(rid: int) -> str:
                    return f"{rid} - Room {room_map.get(rid,'?')} (avail: {avail_map.get(int(rid), 0)})"

                room_id = c2.selectbox("Room", room_choices, format_func=room_label)

                d1, d2, d3 = st.columns(3)
                start_date = d1.date_input("Start Date", value=date.today())
                end_date = d2.date_input("End Date", value=(start_date + timedelta(days=180)))
                status = d3.selectbox("Status", STATUS_OPTS, index=0)

                submitted = st.form_submit_button("Create")
                if submitted:
                    if end_date < start_date:
                        st.error("End Date cannot be before Start Date.")
                    else:
                        # Re-read latest and re-scope to avoid race conditions
                        r_full_latest = rooms_store.list_all()
                        b_full_latest = bookings_store.list_all()
                        if "owner_id" not in r_full_latest.columns: r_full_latest["owner_id"] = None
                        if "owner_id" not in b_full_latest.columns: b_full_latest["owner_id"] = None
                        r_my_latest = r_full_latest[r_full_latest["owner_id"] == uid].copy()
                        b_my_latest = b_full_latest[b_full_latest["owner_id"] == uid].copy()

                        # Capacity check only for ACTIVE
                        if status == "active":
                            latest_avail = _available_beds_per_room_scoped(r_my_latest, b_my_latest).get(int(room_id), 0)
                            if latest_avail <= 0:
                                st.error("Selected room is at full capacity for ACTIVE bookings.")
                                st.stop()

                        # Create (tag owner)
                        bookings_store.create({
                            "owner_id": uid,
                            "student_id": int(student_id),
                            "room_id": int(room_id),
                            "start_date": str(start_date),
                            "end_date": str(end_date),
                            "status": status,
                        })
                        _recompute_room_occupancy_scoped(uid)
                        st.success("Booking created!")
                        st.session_state.show_booking_form = False
                        st.rerun()

        if st.button("Cancel"):
            st.session_state.show_booking_form = False
            st.rerun()

    # ---------- All Bookings (editable, scoped) ----------
    st.write("### My Bookings (editable)")
    b_full_now = bookings_store.list_all()
    if "owner_id" not in b_full_now.columns:
        b_full_now["owner_id"] = None
    b_df = b_full_now[b_full_now["owner_id"] == uid].copy()

    # Friendly display
    if not b_df.empty:
        b_show = b_df.copy()
        b_show["student_name"] = b_show["student_id"].map(student_map)
        b_show["room_no"] = b_show["room_id"].map(room_map)
        b_show = b_show[["id", "student_id", "student_name", "room_id", "room_no", "start_date", "end_date", "status"]]
    else:
        b_show = b_df

    edited = st.data_editor(b_show, key="bookings_editor", num_rows="dynamic", use_container_width=True)

    if st.button("💾 Save booking changes", type="primary"):
        # Convert back to storage format (drop friendly cols)
        if not edited.empty:
            save_df = edited.drop(columns=[c for c in ["student_name", "room_no"] if c in edited.columns]).copy()
            for col in ["id", "student_id", "room_id"]:
                if col in save_df.columns:
                    save_df[col] = pd.to_numeric(save_df[col], errors="coerce").fillna(0).astype(int)
            if "status" in save_df.columns:
                save_df["status"] = save_df["status"].where(save_df["status"].isin(STATUS_OPTS), "active")
        else:
            save_df = edited

        # Merge only my changes back
        _save_scoped(bookings_store.list_all(), save_df, uid, bookings_store)
        _recompute_room_occupancy_scoped(uid)
        st.success("Saved changes.")

    # ---------- Delete (scoped) ----------
    st.write("### Delete Booking by ID (yours only)")
    did = st.text_input("Enter Booking ID", value="", key="booking_delete")
    if st.button("🗑️ Delete"):
        try:
            bid = int(did)
            b_full_now = bookings_store.list_all()
            if "owner_id" not in b_full_now.columns:
                b_full_now["owner_id"] = None
            row = b_full_now[b_full_now["id"] == bid]
            if not row.empty and int(row.iloc[0].get("owner_id", -1)) == uid:
                b_full_now = b_full_now[b_full_now["id"] != bid]
                bookings_store.save_all(b_full_now)
                _recompute_room_occupancy_scoped(uid)
                st.success(f"Deleted booking with id={bid}")
                st.rerun()
            else:
                st.error("You can delete only your own bookings.")
        except ValueError:
            st.error("Enter a valid numeric ID.")

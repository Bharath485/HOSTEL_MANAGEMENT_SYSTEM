import streamlit as st
import pandas as pd
from datetime import date, timedelta
from ..services.booking_service import bookings_store
from ..services.student_service import students_store
from ..services.room_service import rooms_store
from ..utils.lookup import id_to_label

STATUS_OPTS = ["active", "completed", "cancelled"]

def _recompute_room_occupancy():
    r_df = rooms_store.list_all().copy()
    b_df = bookings_store.list_all().copy()
    if r_df.empty:
        return
    if b_df.empty:
        r_df["occupied"] = 0
        rooms_store.save_all(r_df)
        return
    active = b_df[b_df.get("status", "").eq("active")]
    occ = active.groupby("room_id")["id"].count().rename("occ")
    r_df = r_df.merge(occ, how="left", left_on="id", right_index=True)
    r_df["occ"] = r_df["occ"].fillna(0).astype(int)
    r_df["occupied"] = r_df[["occ", "capacity"]].min(axis=1)
    r_df.drop(columns=["occ"], inplace=True)
    rooms_store.save_all(r_df)

def _available_beds_per_room(r_df: pd.DataFrame, b_df: pd.DataFrame) -> dict[int, int]:
    """Compute available beds from capacity - count(active bookings)."""
    if r_df.empty:
        return {}
    active = b_df[b_df.get("status", "").eq("active")] if not b_df.empty else pd.DataFrame()
    counts = active.groupby("room_id")["id"].count().to_dict()
    avail = {}
    for _, r in r_df.iterrows():
        cap = int(r.get("capacity", 0))
        occ = int(counts.get(int(r["id"]), 0))
        avail[int(r["id"])] = max(cap - occ, 0)
    return avail

def show_bookings():
    st.subheader("Bookings")

    # Load latest data
    s_df = students_store.list_all()
    r_df = rooms_store.list_all()
    b_df = bookings_store.list_all()

    if s_df.empty or r_df.empty:
        st.info("Please add at least one Student and one Room before creating bookings.")
        st.stop()

    student_map = id_to_label(s_df, "id", "name")
    room_map = id_to_label(r_df, "id", "room_no")

    # Precompute availability to show in the UI
    avail_map = _available_beds_per_room(r_df, b_df)

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
                student_id = c1.selectbox(
                    "Student",
                    list(student_map.keys()),
                    format_func=lambda k: f"{k} - {student_map.get(k,'')}"
                )

                # Show room with availability e.g., "07 (avail: 2)"
                room_choices = list(room_map.keys())
                def room_label(rid: int) -> str:
                    return f"{rid} - Room {room_map.get(rid,'?')} (avail: {avail_map.get(int(rid), 0)})"

                room_id = c2.selectbox(
                    "Room",
                    room_choices,
                    format_func=room_label
                )

                d1, d2, d3 = st.columns(3)
                start_date = d1.date_input("Start Date", value=date.today())
                # Default end date = start + 6 months
                end_date = d2.date_input("End Date", value=(start_date + timedelta(days=180)))
                status = d3.selectbox("Status", STATUS_OPTS, index=0)

                submitted = st.form_submit_button("Create")
                if submitted:
                    if end_date < start_date:
                        st.error("End Date cannot be before Start Date.")
                    else:
                        # Re-read latest data to avoid race conditions
                        r_df_latest = rooms_store.list_all()
                        b_df_latest = bookings_store.list_all()

                        # Capacity check only for ACTIVE bookings
                        if status == "active":
                            # Compute up-to-the-second availability
                            latest_avail = _available_beds_per_room(r_df_latest, b_df_latest).get(int(room_id), 0)
                            if latest_avail <= 0:
                                st.error("Selected room is at full capacity for ACTIVE bookings.")
                                st.stop()

                        bookings_store.create({
                            "student_id": int(student_id),
                            "room_id": int(room_id),
                            "start_date": str(start_date),
                            "end_date": str(end_date),
                            "status": status,
                        })
                        _recompute_room_occupancy()
                        st.success("Booking created!")
                        st.session_state.show_booking_form = False
                        st.rerun()

        if st.button("Cancel"):
            st.session_state.show_booking_form = False
            st.rerun()

    # ---------- All Bookings (editable with friendly labels) ----------
    st.write("### All Bookings (editable)")
    b_df = bookings_store.list_all()
    if not b_df.empty:
        b_show = b_df.copy()
        b_show["student_name"] = b_show["student_id"].map(student_map)
        b_show["room_no"] = b_show["room_id"].map(room_map)
        b_show = b_show[["id", "student_id", "student_name", "room_id", "room_no", "start_date", "end_date", "status"]]
    else:
        b_show = b_df

    edited = st.data_editor(b_show, key="bookings_editor", num_rows="dynamic", use_container_width=True)

    if st.button("💾 Save booking changes", type="primary"):
        if not edited.empty:
            save_df = edited.drop(columns=[c for c in ["student_name", "room_no"] if c in edited.columns]).copy()
            for col in ["id", "student_id", "room_id"]:
                if col in save_df.columns:
                    save_df[col] = pd.to_numeric(save_df[col], errors="coerce").fillna(0).astype(int)
            if "status" in save_df.columns:
                save_df["status"] = save_df["status"].where(save_df["status"].isin(STATUS_OPTS), "active")
        else:
            save_df = edited

        bookings_store.save_all(save_df)
        _recompute_room_occupancy()
        st.success("Saved changes.")

    # ---------- Delete ----------
    st.write("### Delete Booking by ID")
    did = st.text_input("Enter Booking ID", value="", key="booking_delete")
    if st.button("🗑️ Delete"):
        try:
            bid = int(did)
            bookings_store.delete_by_id(bid)
            _recompute_room_occupancy()
            st.success(f"Deleted booking with id={bid}")
            st.rerun()
        except ValueError:
            st.error("Enter a valid numeric ID.")

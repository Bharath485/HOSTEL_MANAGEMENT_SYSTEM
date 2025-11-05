import streamlit as st
from datetime import date
from ..services.fee_service import fees_store
from ..services.booking_service import bookings_store
from ..services.student_service import students_store
from ..utils.lookup import id_to_label
import pandas as pd

def _recompute_room_occupancy():
    from ..services.room_service import rooms_store
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

def show_fees():
    st.subheader("Fees")

    s_df = students_store.list_all()
    student_map = id_to_label(s_df, "id", "name")

    # ---- Special Payment flow from Rooms (pending booking) ----
    pending = st.session_state.get("pending_booking")
    if pending:
        st.info(f"Payment for Room **{pending['room_no']}** ({pending['room_type']}) — ₹{pending['amount']} for 6 months")
        with st.form("pay_now_form", clear_on_submit=True):
            student_id = st.selectbox(
                "Select Student",
                options=list(student_map.keys()),
                format_func=lambda k: f"{k} - {student_map.get(k, '')}"
            )
            amount = st.number_input("Amount", min_value=0, value=int(pending["amount"]), step=500)
            paid_on = st.date_input("Paid On", value=date.today())
            submitted = st.form_submit_button("Confirm Payment & Create Booking")
            if submitted:
                # 1) record fee as paid
                fees_store.create({
                    "student_id": int(student_id),
                    "month": str(paid_on)[:7],
                    "amount": float(amount),
                    "paid_on": str(paid_on),
                    "status": "paid",
                })
                # 2) create booking
                bookings_store.create({
                    "student_id": int(student_id),
                    "room_id": int(pending["room_id"]),
                    "start_date": pending["start_date"],
                    "end_date": pending["end_date"],
                    "status": "active",
                })
                _recompute_room_occupancy()
                del st.session_state["pending_booking"]
                st.success("Payment recorded and booking created!")
                st.session_state["nav_choice"] = "Bookings"
                st.rerun()

        if st.button("Cancel Payment"):
            del st.session_state["pending_booking"]
            st.warning("Payment cancelled.")
            st.rerun()
        st.write("---")

    # ---- Regular Fees list (editable) ----
    st.write("### All Fees (editable)")
    f_df = fees_store.list_all()
    edited = st.data_editor(f_df, key="fees_editor", num_rows="dynamic", use_container_width=True)
    if st.button("💾 Save fee changes", type="primary"):
        fees_store.save_all(edited)
        st.success("Saved changes.")

    st.write("### Delete Fee by ID")
    did = st.text_input("Enter Fee ID", value="", key="fee_delete")
    if st.button("🗑️ Delete Fee Record"):
        try:
            fid = int(did)
            fees_store.delete_by_id(fid)
            st.success(f"Deleted fee record with id={fid}")
            st.rerun()
        except ValueError:
            st.error("Enter a valid numeric ID.")

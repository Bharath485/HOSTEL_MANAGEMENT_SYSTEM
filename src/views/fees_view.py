import streamlit as st
from datetime import date
from ..services.fee_service import fees_store
from ..services.booking_service import bookings_store
from ..services.student_service import students_store
from ..utils.lookup import id_to_label
import pandas as pd

# --- helper: safe merge so we only update current user's rows ---
def _save_scoped(df_full: pd.DataFrame, df_my: pd.DataFrame, owner_id: int, store) -> None:
    if "owner_id" not in df_full.columns:
        df_full["owner_id"] = None
    if "owner_id" not in df_my.columns:
        df_my["owner_id"] = owner_id
    others = df_full[df_full["owner_id"] != owner_id]
    store.save_all(pd.concat([others, df_my], ignore_index=True))

def _recompute_room_occupancy_scoped(owner_id: int):
    from ..services.room_service import rooms_store
    r_full = rooms_store.list_all().copy()
    b_full = bookings_store.list_all().copy()

    # Ensure columns exist
    if "owner_id" not in r_full.columns: r_full["owner_id"] = None
    if "owner_id" not in b_full.columns: b_full["owner_id"] = None

    r_my = r_full[r_full["owner_id"] == owner_id].copy()
    b_my = b_full[b_full["owner_id"] == owner_id].copy()

    if r_my.empty:
        return

    if b_my.empty:
        r_my["occupied"] = 0
    else:
        active = b_my[b_my.get("status", "").eq("active")]
        occ = active.groupby("room_id")["id"].count().rename("occ")
        r_my = r_my.merge(occ, how="left", left_on="id", right_index=True)
        r_my["occ"] = r_my["occ"].fillna(0).astype(int)
        r_my["occupied"] = r_my[["occ", "capacity"]].min(axis=1)
        r_my.drop(columns=["occ"], inplace=True)

    _save_scoped(r_full, r_my, owner_id, rooms_store)

def show_fees():
    st.subheader("Fees")

    uid = int(st.session_state["user"]["id"])

    # ----- Students: only mine -----
    s_df_full = students_store.list_all()
    if "owner_id" not in s_df_full.columns:
        s_df_full["owner_id"] = None
    s_df = s_df_full[s_df_full["owner_id"] == uid].copy()
    student_map = id_to_label(s_df, "id", "name")

    # ---- Special Payment flow from Rooms (pending booking) ----
    pending = st.session_state.get("pending_booking")
    if pending:
        st.info(
            f"Payment for Room **{pending['room_no']}** ({pending['room_type']}) — "
            f"₹{int(pending['amount'])} for 6 months"
        )
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
                # 1) record fee as paid (scoped to this owner)
                fees_store.create({
                    "owner_id": uid,                       # 👈 tag owner
                    "student_id": int(student_id),
                    "month": str(paid_on)[:7],
                    "amount": float(amount),
                    "paid_on": str(paid_on),
                    "status": "paid",
                })
                # 2) create booking (scoped to this owner)
                bookings_store.create({
                    "owner_id": uid,                       # 👈 tag owner
                    "student_id": int(student_id),
                    "room_id": int(pending["room_id"]),
                    "start_date": pending["start_date"],
                    "end_date": pending["end_date"],
                    "status": "active",
                })
                _recompute_room_occupancy_scoped(uid)
                del st.session_state["pending_booking"]
                st.success("Payment recorded and booking created!")
                st.session_state["nav_choice"] = "Bookings"
                st.rerun()

        if st.button("Cancel Payment"):
            del st.session_state["pending_booking"]
            st.warning("Payment cancelled.")
            st.rerun()
        st.write("---")

    # ---- Regular Fees list (editable, only mine) ----
    st.write("### My Fees (editable)")
    f_full = fees_store.list_all()
    if "owner_id" not in f_full.columns:
        f_full["owner_id"] = None
    f_df = f_full[f_full["owner_id"] == uid].copy()

    edited = st.data_editor(f_df, key="fees_editor", num_rows="dynamic", use_container_width=True)

    if st.button("💾 Save fee changes", type="primary"):
        # Merge only my edits back to the full CSV
        _save_scoped(f_full, edited, uid, fees_store)
        st.success("Saved changes.")

    st.write("### Delete Fee by ID (yours only)")
    did = st.text_input("Enter Fee ID", value="", key="fee_delete")
    if st.button("🗑️ Delete Fee Record"):
        try:
            fid = int(did)
            # allow delete only if the row belongs to current user
            f_full = fees_store.list_all()
            if "owner_id" not in f_full.columns:
                f_full["owner_id"] = None
            row = f_full[f_full["id"] == fid]
            if not row.empty and int(row.iloc[0].get("owner_id", -1)) == uid:
                f_full = f_full[f_full["id"] != fid]
                fees_store.save_all(f_full)
                st.success(f"Deleted fee record with id={fid}")
                st.rerun()
            else:
                st.error("You can delete only your own records.")
        except ValueError:
            st.error("Enter a valid numeric ID.")

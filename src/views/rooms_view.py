import streamlit as st
from ..services.room_service import rooms_store
from ..utils.seed_rooms import generate_default_rooms  # make sure it accepts owner_id

TYPE_CAPACITY = {"Double": 2, "Triple": 3}
TYPE_PRICE   = {"Double": 50000, "Triple": 40000}  # per 6 months

def show_rooms():
    st.subheader("Rooms")

    # Logged-in user
    uid = int(st.session_state["user"]["id"])

    with st.expander("🏗️ One-time Setup", expanded=False):
        st.caption("Generate a fixed inventory for YOUR hostel: 01–50 Triple (3-share), 51–100 Double (2-share).")
        if st.button("Generate 100 Rooms (01–100) for Me"):
            # ✅ ensure your seeder creates rows with owner_id=uid
            created = generate_default_rooms(owner_id=uid)
            if created:
                st.success("Rooms generated for your account.")
            else:
                st.info("You already have rooms. Skipped.")
            st.rerun()

    st.write("### My Rooms")

    # ✅ show only this user's rooms
    df = rooms_store.list_all()
    if "owner_id" not in df.columns:
        df["owner_id"] = None
    df = df[df["owner_id"] == uid].copy()

    if df.empty:
        st.info("No rooms for your account yet. Use the setup button above to generate your 100 rooms.")
        return

    # Capacity-aware “Book & Pay” button (hidden if full)
    for _, row in df.iterrows():
        with st.container():
            cap = int(row.get("capacity", 0))
            occ = int(row.get("occupied", 0))
            available = max(cap - occ, 0)
            price = TYPE_PRICE.get(str(row["type"]), 0)

            c1, c2, c3, c4, c5, c6 = st.columns([1.3, 1, 1, 1, 1.4, 1.2])
            c1.write(f"**{row['room_no']}**")
            c2.write(str(row["type"]))
            c3.write(f"Cap: {cap}")
            c4.write(f"Occ: {occ}")

            if available <= 0:
                c5.write("**Status:** Full")
                c6.button("Booked", key=f"full_{int(row['id'])}", disabled=True)
            else:
                c5.write(f"**Available:** {available}")
                if c6.button(f"Book & Pay (₹{price})", key=f"book_{int(row['id'])}"):
                    from datetime import date, timedelta
                    st.session_state["pending_booking"] = {
                        "owner_id": uid,                       # ✅ carry owner forward
                        "room_id": int(row["id"]),
                        "room_no": str(row["room_no"]),
                        "room_type": str(row["type"]),
                        "amount": int(price),
                        "start_date": str(date.today()),
                        "end_date": str(date.today() + timedelta(days=180)),
                        "status": "active",
                    }
                    st.session_state["nav_choice"] = "Fees"
                    st.rerun()

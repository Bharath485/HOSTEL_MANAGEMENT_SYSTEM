import streamlit as st
from ..services.room_service import rooms_store
from ..services.student_service import students_store
from ..services.booking_service import bookings_store

def show_dashboard():
    st.title("🏨 Welcome to the Hostel")

    # Logged-in user
    uid = int(st.session_state["user"]["id"])

    # Fetch & scope to current user (safe if old CSVs miss owner_id)
    students = students_store.list_all()
    rooms = rooms_store.list_all()
    bookings = bookings_store.list_all()

    for df in (students, rooms, bookings):
        if "owner_id" not in df.columns:
            df["owner_id"] = None

    students = students[students["owner_id"] == uid].copy()
    rooms    = rooms[rooms["owner_id"] == uid].copy()
    bookings = bookings[bookings["owner_id"] == uid].copy()

    total_rooms = len(rooms)

    # ---- Vacant beds overall
    if not rooms.empty:
        rooms["capacity"] = rooms["capacity"].fillna(0).astype(int)
        rooms["occupied"] = rooms["occupied"].fillna(0).astype(int)
        vacant_beds = int((rooms["capacity"] - rooms["occupied"]).clip(lower=0).sum())
    else:
        vacant_beds = 0

    st.write(f"### Total Rooms Available: **{total_rooms}**")

    st.write("---")
    st.subheader("Room Segments Available")

    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        **2-Sharing Room**
        - Capacity: 2 Students
        - Fee: **₹50,000** / 6 months
        """)
    with col2:
        st.info("""
        **3-Sharing Room**
        - Capacity: 3 Students
        - Fee: **₹40,000** / 6 months
        """)

    st.write("---")

    # ---- Top metrics (now includes Vacant Beds)
    colA, colB, colC, colD = st.columns(4)
    colA.metric("Total Students", len(students))
    colB.metric("Total Rooms", total_rooms)
    colC.metric("Active Bookings",
                int((bookings["status"] == "active").sum()) if not bookings.empty else 0)
    colD.metric("Vacant Beds", vacant_beds)

    # ---- Optional: segment-wise vacancy
    st.caption("Vacancy by segment")
    seg = rooms.copy()
    if not seg.empty:
        seg["vacant"] = (seg["capacity"] - seg["occupied"]).clip(lower=0)
        v2 = int(seg.loc[seg["type"] == "Double", "vacant"].sum())
        v3 = int(seg.loc[seg["type"] == "Triple", "vacant"].sum())
        s1, s2 = st.columns(2)
        s1.metric("Double (2-share) vacant", v2)
        s2.metric("Triple (3-share) vacant", v3)

    st.write("---")

    # ---- Recent tables
    st.write("### Recent Students")
    st.dataframe(students.tail(5), width=True)

    st.write("### Recent Bookings")
    st.dataframe(bookings.tail(5), width=True)

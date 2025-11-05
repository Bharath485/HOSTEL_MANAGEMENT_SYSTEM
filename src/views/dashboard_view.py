import streamlit as st
from ..services.room_service import rooms_store
from ..services.student_service import students_store
from ..services.booking_service import bookings_store

def show_dashboard():
    st.title("🏨 Welcome to the Hostel")

    # Fetch Data
    students = students_store.list_all()
    rooms = rooms_store.list_all()
    bookings = bookings_store.list_all()

    total_rooms = len(rooms)

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

    colA, colB, colC = st.columns(3)

    colA.metric("Total Students", len(students))
    colB.metric("Total Rooms", total_rooms)
    colC.metric("Active Bookings", (bookings["status"] == "active").sum() if not bookings.empty else 0)

    st.write("---")

    st.write("### Recent Students")
    st.dataframe(students.tail(5))

    st.write("### Recent Bookings")
    st.dataframe(bookings.tail(5))

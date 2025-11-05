
import streamlit as st
from ..services.student_service import students_store
from ..services.room_service import rooms_store
from ..services.booking_service import bookings_store

def show_dashboard():
    st.subheader("Dashboard")
    s_df = students_store.list_all()
    r_df = rooms_store.list_all()
    b_df = bookings_store.list_all()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students", len(s_df))
    col2.metric("Rooms", len(r_df))
    active_bookings = (b_df["status"] == "active").sum() if "status" in b_df else 0
    col3.metric("Active Bookings", int(active_bookings))

    st.write("### Quick Peek")
    st.write("#### Students")
    st.dataframe(s_df.tail(5))
    st.write("#### Rooms")
    st.dataframe(r_df.tail(5))

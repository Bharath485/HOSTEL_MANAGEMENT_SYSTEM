
import streamlit as st
from src.views.dashboard_view import show_dashboard
from src.views.students_view import show_students
from src.views.rooms_view import show_rooms
from src.views.bookings_view import show_bookings
from src.views.fees_view import show_fees

st.set_page_config(page_title="Hostel Management System", page_icon="🏨", layout="wide")

PAGES = {
    "Dashboard": show_dashboard,
    "Students": show_students,
    "Rooms": show_rooms,
    "Bookings": show_bookings,
    "Fees": show_fees,
}

with st.sidebar:
    st.title("🏨 Hostel MS")
    choice = st.selectbox("Navigate", list(PAGES.keys()))

# Render selected page
PAGES[choice]()

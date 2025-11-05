import streamlit as st
from src.views.auth_view import show_login, show_signup
from src.views.dashboard_view import show_dashboard
from src.views.students_view import show_students
from src.views.rooms_view import show_rooms
from src.views.bookings_view import show_bookings
from src.views.fees_view import show_fees

st.set_page_config(page_title="Hostel Management System", page_icon="🏨", layout="wide")

# Login gate
if "user" not in st.session_state:
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Sign Up"])
    with tab1: show_login()
    with tab2: show_signup()
    st.stop()

# Simple nav state to allow programmatic routing
if "nav_choice" not in st.session_state:
    st.session_state["nav_choice"] = "Dashboard"

def go(page: str):
    st.session_state["nav_choice"] = page
    st.rerun()

with st.sidebar:
    st.title("🏨 Hostel MS")
    st.write(f"👤 {st.session_state['user']['name']}")
    choice = st.selectbox(
        "Navigate",
        ["Dashboard", "Students", "Rooms", "Bookings", "Fees"],
        index=["Dashboard", "Students", "Rooms", "Bookings", "Fees"].index(st.session_state["nav_choice"])
    )
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
    if choice != st.session_state["nav_choice"]:
        st.session_state["nav_choice"] = choice
        st.rerun()

page = st.session_state["nav_choice"]
if page == "Dashboard": show_dashboard()
elif page == "Students": show_students()
elif page == "Rooms": show_rooms()
elif page == "Bookings": show_bookings()
elif page == "Fees": show_fees()

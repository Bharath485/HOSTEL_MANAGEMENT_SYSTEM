
import streamlit as st
from ..services.booking_service import bookings_store

def show_bookings():
    st.subheader("Bookings (Starter Stub)")
    st.info("This section is scaffolded. Add booking create/list logic here (CSV columns already defined).")
    st.dataframe(bookings_store.list_all())

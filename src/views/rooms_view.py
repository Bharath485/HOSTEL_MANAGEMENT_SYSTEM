
import streamlit as st
from ..services.room_service import rooms_store

def show_rooms():
    st.subheader("Rooms")
    with st.expander("➕ Add Room", expanded=True):
        with st.form("add_room_form", clear_on_submit=True):
            room_no = st.text_input("Room No")
            rtype = st.selectbox("Type", ["Single", "Double", "Dorm"])
            capacity = st.number_input("Capacity", min_value=1, step=1, value=2)
            occupied = st.number_input("Occupied", min_value=0, step=1, value=0)
            submitted = st.form_submit_button("Add")
            if submitted:
                rooms_store.create({
                    "room_no": room_no, "type": rtype,
                    "capacity": int(capacity), "occupied": int(occupied)
                })
                st.success("Room added!")

    st.write("### All Rooms")
    st.dataframe(rooms_store.list_all())

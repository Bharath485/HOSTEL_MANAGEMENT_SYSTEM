
import streamlit as st
from ..services.student_service import students_store

def show_students():
    st.subheader("Students")
    with st.expander("➕ Add Student", expanded=True):
        with st.form("add_student_form", clear_on_submit=True):
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            course = st.text_input("Course / Dept")
            submitted = st.form_submit_button("Add")
            if submitted:
                students_store.create({
                    "name": name, "email": email, "phone": phone,
                    "gender": gender, "course": course
                })
                st.success("Student added!")

    st.write("### All Students")
    st.dataframe(students_store.list_all())

import streamlit as st
from ..services.student_service import students_store

def show_students():
    st.subheader("Students")

    # Logged in user's id
    uid = st.session_state["user"]["id"]

    with st.expander("➕ Add Student", expanded=False):
        with st.form("add_student_form", clear_on_submit=True):
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            course = st.text_input("Course / Dept")
            submitted = st.form_submit_button("Add")
            if submitted:
                students_store.create({
                    "owner_id": uid,   # ✅ store who added this student
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "gender": gender,
                    "course": course
                })
                st.success("Student added!")

    st.write("### My Students")

    # ✅ Show only current user's data
    df = students_store.list_all()

    # If the column didn't exist previously, create empty
    if "owner_id" not in df.columns:
        df["owner_id"] = None

    df = df[df["owner_id"] == uid]   # ✅ filter

    st.dataframe(df, width=True)

import streamlit as st
from ..services.auth_service import users_store
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def show_signup():
    st.subheader("Create Account")
    with st.form("signup_form", clear_on_submit=True):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign Up")

        if submitted:
            if not name or not email or not password:
                st.error("All fields are required")
            else:
                users_store.create({
                    "name": name,
                    "email": email,
                    "password": hash_password(password)
                })
                st.success("Account created successfully! Please login.")

def show_login():
    st.subheader("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            df = users_store.list_all()
            hashed = hash_password(password)

            user = df[(df["email"] == email) & (df["password"] == hashed)]

            if not user.empty:
                st.session_state["user"] = {
                    "id": int(user.iloc[0]["id"]),
                    "name": user.iloc[0]["name"],
                    "email": user.iloc[0]["email"]
                }
                st.success(f"Welcome, {user.iloc[0]['name']}!")
                st.rerun()
            else:
                st.error("Invalid email or password")

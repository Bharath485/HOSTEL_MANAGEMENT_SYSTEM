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
            name = (name or "").strip()
            email_norm = (email or "").strip().lower()
            pwd = (password or "").strip()

            if not name or not email_norm or not pwd:
                st.error("All fields are required")
                return

            # Duplicate email check (case-insensitive)
            df = users_store.list_all()
            if "email" in df.columns:
                if (df["email"].str.lower() == email_norm).any():
                    st.error("An account with this email already exists.")
                    return

            # New users are admins by requirement
            users_store.create({
                "name": name,
                "email": email_norm,
                "password": hash_password(pwd),
                "role": "admin",     # ✅ make every new signup an admin
            })
            st.success("Account created successfully! Please login.")

def show_login():
    st.subheader("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            email_norm = (email or "").strip().lower()
            pwd = (password or "").strip()

            df = users_store.list_all()
            if "email" in df.columns:
                df = df.copy()
                # normalize email column for comparison
                df["__email_norm__"] = df["email"].astype(str).str.lower()
                hashed = hash_password(pwd)

                user = df[(df["__email_norm__"] == email_norm) & (df["password"] == hashed)]

                if not user.empty:
                    st.session_state["user"] = {
                        "id": int(user.iloc[0]["id"]),
                        "name": user.iloc[0]["name"],
                        "email": user.iloc[0]["email"],
                        "role": user.iloc[0].get("role", "admin"),  # ✅ keep role in session
                    }
                    st.success(f"Welcome, {user.iloc[0]['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
            else:
                st.error("User store is not initialized properly.")

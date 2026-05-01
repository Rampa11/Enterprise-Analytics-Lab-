import streamlit as st
from auth import supabase
from db import upsert_user

st.title("Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):

    try:
        res = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        st.session_state["user"] = res.user.email
        st.session_state["user_id"] = res.user.id

        upsert_user(res.user.email, res.user.id)

        st.success("Login successful")

        st.switch_page("dashboard.py")

    except Exception as e:
        st.error("Login failed")

st.divider()

st.subheader("Create Account")

new_email = st.text_input("Email", key="signup_email")
new_password = st.text_input("Password", type="password", key="signup_pass")

if st.button("Sign Up"):

    try:
        supabase.auth.sign_up(
            {"email": new_email, "password": new_password}
        )

        st.success("Account created")

    except:
        st.error("Signup failed")        
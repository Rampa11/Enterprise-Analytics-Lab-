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

        # 🔥 FIXED CONDITION
        if res and res.session:

            st.session_state["user"] = email
            st.session_state["user_id"] = res.session.user.id

            st.success("Login successful")

            st.switch_page("dashboard.py")

        else:
            st.error("Invalid login credentials")

    except Exception as e:
        st.error(f"Login failed: {e}")

st.divider()

st.subheader("Create Account")

new_email = st.text_input("Email", key="signup_email")
new_password = st.text_input("Password", type="password", key="signup_pass")

full_name = st.text_input("Full Name")
dob = st.date_input("Date of Birth")

if st.button("Sign Up"):

    try:
        res = supabase.auth.sign_up({
            "email": new_email,
            "password": new_password
        })

        if res.user:
            # 🔥 Save extra info to your DB
            supabase.table("users_profile").insert({
                "id": res.user.id,
                "email": new_email,
                "full_name": full_name,
                "dob": str(dob),
                "plan": "free",
                "credits": 0
            }).execute()

            st.success("Account created. Check your email to verify.")

        else:
            st.error("Signup failed")

    except Exception as e:
        st.error(f"Signup error: {e}") 
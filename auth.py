"""A separate auth client for each Streamlit session; never share login state."""
import streamlit as st
from supabase import create_client
from lab.config import setting

def get_client():
    url, key = setting("SUPABASE_URL"), setting("SUPABASE_ANON_KEY") or setting("SUPABASE_KEY")
    if not url or not key:
        return None
    if "_auth_client" not in st.session_state:
        st.session_state["_auth_client"] = create_client(url, key)
    return st.session_state["_auth_client"]

def current_user():
    return st.session_state.get("account")

def verify_user():
    client = get_client()
    if not client or not current_user():
        raise RuntimeError("Sign in to continue.")
    user = client.auth.get_user().user
    if not user or user.id != current_user()["id"]:
        raise RuntimeError("Your session expired. Sign in again.")
    return user

def sign_in(email, password):
    client = get_client()
    if not client:
        raise RuntimeError("Account services are not configured.")
    response = client.auth.sign_in_with_password({"email":email.strip(),"password":password})
    if not response.session:
        raise RuntimeError("Confirm your email before signing in.")
    st.session_state.clear()
    st.session_state["_auth_client"] = client
    user = response.user
    st.session_state["account"] = {"id":user.id,"email":user.email,"name":user.user_metadata.get("full_name","Analyst")}
    return user

def sign_out():
    client = get_client()
    try:
        if client:
            client.auth.sign_out()
    finally:
        st.session_state.clear()

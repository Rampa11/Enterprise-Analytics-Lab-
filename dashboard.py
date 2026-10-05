"""Streamlit entry point: page configuration precedes UI calls."""
import streamlit as st
st.set_page_config(page_title="Enterprise Analytics Lab",page_icon=":material/analytics:",layout="wide")
from lab.ui import apply_style,sidebar,footer
from lab.home import home
apply_style()
sidebar()
if st.query_params.get("checkout")=="returned":
    st.info("Welcome back. Payment confirmation is processing. Open Learning plans and refresh your status.")
    st.query_params.clear()
if st.session_state.get("account_notice"):
    st.warning(st.session_state.pop("account_notice"))
pages={
 "WORKSPACE":[st.Page(home,title="Overview",icon=":material/dashboard:",default=True),st.Page("pages/Industry_Selection.py",title="Industry library",icon=":material/grid_view:")],
 "LEARN":[st.Page("pages/Practice_Lab.py",title="Practice lab",icon=":material/science:"),st.Page("pages/AI_Business_Manager.py",title="Business manager",icon=":material/work:"),st.Page("pages/Daily_Challenge.py",title="Daily challenge",icon=":material/today:")],
 "GROW":[st.Page("pages/AI_Dataset_Generator.py",title="Dataset studio",icon=":material/table_chart:"),st.Page("pages/Profile.py",title="My progress",icon=":material/trending_up:"),st.Page("pages/Leaderboard.py",title="Leaderboard",icon=":material/leaderboard:")],
 "ACCOUNT":[st.Page("pages/Pricing.py",title="Learning plans",icon=":material/diamond:"),st.Page("pages/Login.py",title="Account",icon=":material/account_circle:")]
}
st.navigation(pages).run()
footer()

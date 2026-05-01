import streamlit as st
from ai_engine.daily_challenge import get_daily_challenge

st.title("Daily Data Challenge")

challenge = get_daily_challenge()

st.subheader("Today's Challenge")

st.info(challenge)

answer = st.text_area("Submit your analysis")

if st.button("Submit Challenge"):

    st.success("Challenge submitted! XP will be awarded after grading.")
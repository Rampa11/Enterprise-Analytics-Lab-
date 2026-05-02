import streamlit as st
import pandas as pd
from ai_engine.leaderboard import get_top_scores

st.title("Top Data Analysts")

scores = get_top_scores()

if len(scores) == 0:

    st.info("No scores yet.")
    st.stop()


df = pd.DataFrame(scores)

df = df.sort_values("score", ascending=False)

st.dataframe(
    df[["user_email", "industry", "score", "xp"]]
)
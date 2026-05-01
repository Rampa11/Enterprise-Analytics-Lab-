import streamlit as st

st.title("Select Industry")

industry = st.selectbox(
    "Choose an industry to practice analytics",
    [
        "Oil & Gas",
        "Healthcare",
        "Manufacturing",
        "Food & Beverage",
        "Logistics"
    ]
)

if st.button("Load Industry"):
    st.session_state["industry"] = industry
    st.success(f"{industry} dataset loaded")
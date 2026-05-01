import pandas as pd
import streamlit as st

def load_industry_data():

    if "industry" not in st.session_state:
        return None

    industry = st.session_state["industry"]

    if industry == "Oil & Gas":
        return pd.read_csv("data/oil_gas/production.csv")

    if industry == "Healthcare":
        return pd.read_csv("data/healthcare/hospital_metrics.csv")

    if industry == "Manufacturing":
        return pd.read_csv("data/manufacturing/factory_output.csv")

    if industry == "Food & Beverage":
        return pd.read_csv("data/food_beverage/sales.csv")

    if industry == "Logistics":
        return pd.read_csv("data/logistics/shipments.csv")
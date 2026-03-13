import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv

st.title("Enterprise Analytics Platform")

# -------- Detect Environment -------- #

LOCAL = os.path.exists(".env")

# -------- Local Mode (PostgreSQL) -------- #

if LOCAL:

    load_dotenv()

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    revenue_query = """
    SELECT SUM(p.price * f.quantity) AS total_revenue
    FROM fact_sales f
    JOIN dim_products p ON f.product_id = p.product_id;
    """

    revenue = pd.read_sql(revenue_query, engine)

    top_products_query = """
    SELECT p.product_name, SUM(f.quantity) AS units_sold
    FROM fact_sales f
    JOIN dim_products p ON f.product_id = p.product_id
    GROUP BY p.product_name
    ORDER BY units_sold DESC
    LIMIT 10;
    """

    top_products = pd.read_sql(top_products_query, engine)

    inventory = pd.read_sql(
        "SELECT product_id, stock_level, reorder_level FROM inventory WHERE stock_level < reorder_level;",
        engine,
    )

    ops = pd.read_sql(
        "SELECT warehouse_id, AVG(delivery_time_hours) AS avg_delivery_time FROM operations GROUP BY warehouse_id;",
        engine,
    )

# -------- Cloud Mode (CSV files) -------- #

else:

    sales = pd.read_csv("sales.csv")
    products = pd.read_csv("products.csv")
    inventory = pd.read_csv("inventory.csv")
    ops = pd.read_csv("operations.csv")

    merged = sales.merge(products, on="product_id")

    revenue = pd.DataFrame({
        "total_revenue": [(merged["price"] * merged["quantity"]).sum()]
    })

    top_products = (
        merged.groupby("product_name")["quantity"]
        .sum()
        .reset_index(name="units_sold")
        .sort_values("units_sold", ascending=False)
        .head(10)
    )

    inventory = inventory[inventory["stock_level"] < inventory["reorder_level"]]

    ops = (
        ops.groupby("warehouse_id")["delivery_time_hours"]
        .mean()
        .reset_index(name="avg_delivery_time")
    )

# -------- Dashboard -------- #

st.header("Key Metrics")

st.metric("Total Revenue", f"${int(revenue.iloc[0,0]):,}")

st.header("Top Selling Products")

fig = px.bar(top_products, x="product_name", y="units_sold")
st.plotly_chart(fig)

st.header("Inventory Risk Alerts")

st.dataframe(inventory)

st.header("Warehouse Delivery Performance")

fig2 = px.bar(ops, x="warehouse_id", y="avg_delivery_time")
st.plotly_chart(fig2)
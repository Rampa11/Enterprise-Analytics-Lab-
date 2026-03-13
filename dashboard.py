import streamlit as st
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ---------------- KPI SECTION ---------------- #

st.header("Key Metrics")

revenue_query = """
SELECT SUM(p.price * f.quantity) AS total_revenue
FROM fact_sales f
JOIN dim_products p ON f.product_id = p.product_id;
"""

revenue = pd.read_sql(revenue_query, engine)

total_revenue = revenue.iloc[0, 0]

st.metric("Total Revenue", f"${int(total_revenue):,}")

# ---------------- TOP PRODUCTS ---------------- #

st.header("Top Selling Products")

top_products_query = """
SELECT p.product_name, SUM(f.quantity) AS units_sold
FROM fact_sales f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY units_sold DESC
LIMIT 10;
"""

top_products = pd.read_sql(top_products_query, engine)

fig = px.bar(
    top_products,
    x="product_name",
    y="units_sold",
    title="Top Selling Products"
)

st.plotly_chart(fig)

# ---------------- INVENTORY ALERTS ---------------- #

st.header("Inventory Risk Alerts")

inventory_query = """
SELECT product_id, stock_level, reorder_level
FROM inventory
WHERE stock_level < reorder_level;
"""

inventory = pd.read_sql(inventory_query, engine)

st.dataframe(inventory)

# ---------------- OPERATIONS PERFORMANCE ---------------- #

st.header("Warehouse Delivery Performance")

ops_query = """
SELECT warehouse_id,
AVG(delivery_time_hours) AS avg_delivery_time
FROM operations
GROUP BY warehouse_id;
"""

ops = pd.read_sql(ops_query, engine)

fig2 = px.bar(
    ops,
    x="warehouse_id",
    y="avg_delivery_time",
    title="Average Delivery Time by Warehouse"
)

st.plotly_chart(fig2)
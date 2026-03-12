# Enterprise Analytics Pipeline

An end-to-end analytics platform that simulates how organizations analyze sales, inventory, and operational performance using Python, PostgreSQL, and SQL analytics.

![Python](https://img.shields.io/badge/Python-Data%20Pipeline-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Data%20Warehouse-blue)
![SQL](https://img.shields.io/badge/SQL-Analytics-green)
![PowerBI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow)

---
## Project Architecture

Python Data Generator  
↓  
Raw CSV Data  
↓  
PostgreSQL Data Warehouse  
↓  
Analytics Views  
↓  
Power BI / Tableau Dashboards  

## Data Pipeline

1. Python generates synthetic operational datasets.
2. CSV files simulate data exports from operational systems.
3. Data is loaded into a PostgreSQL warehouse.
4. SQL analytics views transform raw data into business KPIs.
5. Dashboards visualize insights for decision makers.

## Overview

This project demonstrates an end-to-end enterprise analytics pipeline that simulates how organizations analyze operational data across Sales, Inventory, and Operations.

Operational data is generated using Python, stored as CSV files, loaded into a PostgreSQL data warehouse using a star schema, and transformed into analytics views that power business dashboards.

## Tech Stack

- Python
- PostgreSQL
- SQL
- Power BI / Tableau 

## Data Model

### Fact Table
- fact_sales

Dimension Tables

- dim_products
- dim_customers

Operational Tables

- inventory
- operations

## Analytics Views

- sales_summary
- product_performance
- inventory_alerts
- operations_summary

## Business Insights

The platform answers key business questions:

- What products generate the most revenue?
- Which customers drive the most demand?
- Which warehouses have slow delivery times?
- Which products are at risk of stockout?

## Skills Demonstrated

- Data Modeling
- SQL Analytics
- ETL Pipeline Design
- Business KPI Development
- Operational Analytics

## Demo Insights

After loading the generated datasets into the PostgreSQL warehouse, the analytics layer produces the following example insights.

### Top Selling Products

```sql
SELECT p.product_name, SUM(f.quantity) AS units_sold
FROM fact_sales f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY units_sold DESC
LIMIT 10;
```

### Revenue KPI

```sql
SELECT SUM(p.price * f.quantity) AS total_revenue
FROM fact_sales f
JOIN dim_products p ON f.product_id = p.product_id;
```

### Inventory Risk

Products below reorder level.

```sql
SELECT product_id, stock_level, reorder_level
FROM inventory
WHERE stock_level < reorder_level;
```

### Operations Performance

Average delivery time by warehouse.

```sql
SELECT warehouse_id,
AVG(delivery_time_hours) AS avg_delivery_time
FROM operations
GROUP BY warehouse_id;
```

## Example Business Questions Answered

* Which products generate the most revenue?
* Which customers drive the highest demand?
* Which warehouses have slow delivery performance?
* Which products are at risk of stockout?

These insights power dashboards used by operations managers, sales teams, and executives.

## Getting Started

1. Generate the synthetic datasets.

```bash
python generate_data.py
```

2. Connect to PostgreSQL and create the analytics database.

```bash
psql -U postgres
```

```sql
CREATE DATABASE enterprise_analytics;
```

3. Create the warehouse tables (Star Schema).

Run the schema SQL script or execute the table creation statements for:

* dim_products
* dim_customers
* fact_sales
* inventory
* operations

4. Load the generated CSV datasets into PostgreSQL.

Example command using `psql`:

```sql
\copy fact_sales FROM 'sales.csv' DELIMITER ',' CSV HEADER;
```

Repeat the process for:

* products.csv
* customers.csv
* inventory.csv
* operations.csv

5. Connect a BI tool to the database.

Use either **Power BI** or **Tableau** to connect to the PostgreSQL database and build dashboards using the analytics views:

* sales_summary
* product_performance
* inventory_alerts
* operations_summary



# Enterprise Analytics Pipeline

## Overview

This project demonstrates an end-to-end enterprise analytics pipeline that simulates how organizations analyze operational data across Sales, Inventory, and Operations.

The system ingests operational data, loads it into a PostgreSQL warehouse using a star schema, and generates analytical views that power business dashboards.

## Architecture

Data Generation → PostgreSQL Warehouse → Analytics Views → Dashboards

## Tech Stack

Python
PostgreSQL
SQL
Power BI / Tableau

## Data Model

Fact Table

* fact_sales

Dimension Tables

* dim_products
* dim_customers

Operational Tables

* inventory
* operations

## Analytics Views

sales_summary
product_performance
inventory_alerts
operations_summary

## Business Insights

The platform answers key business questions:

* What products generate the most revenue?
* Which customers drive the most demand?
* Which warehouses have slow delivery times?
* Which products are at risk of stockout?

## Skills Demonstrated

Data Modeling
SQL Analytics
ETL Pipeline Design
Business KPI Development
Operational Analytics

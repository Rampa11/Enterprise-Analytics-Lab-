CREATE TABLE dim_products (
product_id TEXT PRIMARY KEY,
product_name TEXT,
price INTEGER
);

CREATE TABLE dim_customers (
customer_id TEXT PRIMARY KEY,
customer_name TEXT
);

CREATE TABLE fact_sales (
order_id TEXT PRIMARY KEY,
product_id TEXT,
customer_id TEXT,
quantity INTEGER
);

CREATE TABLE inventory (
product_id TEXT PRIMARY KEY,
warehouse_id TEXT,
stock_level INTEGER,
reorder_level INTEGER
);

CREATE TABLE operations (
order_id TEXT PRIMARY KEY,
warehouse_id TEXT,
processing_time_hours INTEGER,
shipping_time_hours INTEGER,
delivery_time_hours INTEGER
);
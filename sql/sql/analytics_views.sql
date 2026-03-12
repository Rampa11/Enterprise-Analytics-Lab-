CREATE VIEW sales_summary AS
SELECT
COUNT(f.order_id) AS total_orders,
SUM(f.quantity) AS total_units_sold,
SUM(p.price * f.quantity) AS total_revenue
FROM fact_sales f
JOIN dim_products p
ON f.product_id = p.product_id;

CREATE VIEW product_performance AS
SELECT
p.product_name,
SUM(f.quantity) AS units_sold,
SUM(p.price * f.quantity) AS revenue
FROM fact_sales f
JOIN dim_products p
ON f.product_id = p.product_id
GROUP BY p.product_name;

CREATE VIEW inventory_alerts AS
SELECT *
FROM inventory
WHERE stock_level < reorder_level;

CREATE VIEW operations_summary AS
SELECT
warehouse_id,
AVG(processing_time_hours) AS avg_processing_time,
AVG(delivery_time_hours) AS avg_delivery_time
FROM operations
GROUP BY warehouse_id;
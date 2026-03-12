import pandas as pd
import random
from faker import Faker

fake = Faker()

NUM_PRODUCTS = 500
NUM_CUSTOMERS = 2000
NUM_ORDERS = 50000

WAREHOUSES = ["W1","W2","W3","W4","W5"]

products = []
customers = []
sales = []
inventory = []
operations = []

# PRODUCTS
for i in range(NUM_PRODUCTS):
    products.append({
        "product_id": f"P{i+1}",
        "product_name": fake.word(),
        "price": random.randint(20,1500)
    })

# CUSTOMERS
for i in range(NUM_CUSTOMERS):
    customers.append({
        "customer_id": f"C{i+1}",
        "customer_name": fake.name()
    })

# SALES
for i in range(NUM_ORDERS):
    product = random.choice(products)

    sales.append({
        "order_id": f"O{i+1}",
        "product_id": product["product_id"],
        "customer_id": random.choice(customers)["customer_id"],
        "quantity": random.randint(1,5)
    })

# INVENTORY
for p in products:
    inventory.append({
        "product_id": p["product_id"],
        "warehouse_id": random.choice(WAREHOUSES),
        "stock_level": random.randint(0,500),
        "reorder_level": random.randint(20,100)
    })

# OPERATIONS
for s in sales:
    operations.append({
        "order_id": s["order_id"],
        "warehouse_id": random.choice(WAREHOUSES),
        "processing_time_hours": random.randint(1,48),
        "shipping_time_hours": random.randint(24,120),
        "delivery_time_hours": random.randint(48,240)
    })

pd.DataFrame(products).to_csv("products.csv", index=False)
pd.DataFrame(customers).to_csv("customers.csv", index=False)
pd.DataFrame(sales).to_csv("sales.csv", index=False)
pd.DataFrame(inventory).to_csv("inventory.csv", index=False)
pd.DataFrame(operations).to_csv("operations.csv", index=False)

print("Enterprise datasets generated successfully.")
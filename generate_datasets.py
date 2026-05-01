import pandas as pd
import numpy as np
import os

np.random.seed(42)

rows = 5000

# Create directories
os.makedirs("data/oil_gas", exist_ok=True)
os.makedirs("data/healthcare", exist_ok=True)
os.makedirs("data/manufacturing", exist_ok=True)
os.makedirs("data/food_beverage", exist_ok=True)
os.makedirs("data/logistics", exist_ok=True)

# ----------------------------
# OIL & GAS
# ----------------------------

oil = pd.DataFrame({
    "well_id": np.random.randint(1000, 2000, rows),
    "region": np.random.choice(["North", "South", "East", "West"], rows),
    "production_barrels": np.random.randint(500, 5000, rows),
    "operational_cost": np.random.randint(20000, 200000, rows),
    "downtime_hours": np.random.randint(0, 48, rows)
})

oil.to_csv("data/oil_gas/production.csv", index=False)


# ----------------------------
# HEALTHCARE
# ----------------------------

health = pd.DataFrame({
    "hospital_id": np.random.randint(1, 50, rows),
    "department": np.random.choice(["Emergency", "Cardiology", "Pediatrics"], rows),
    "patients_per_day": np.random.randint(20, 300, rows),
    "avg_wait_time_minutes": np.random.randint(5, 120, rows),
    "treatment_cost": np.random.randint(100, 5000, rows)
})

health.to_csv("data/healthcare/hospital_metrics.csv", index=False)


# ----------------------------
# MANUFACTURING
# ----------------------------

manufacturing = pd.DataFrame({
    "factory_id": np.random.randint(1, 20, rows),
    "product": np.random.choice(["Cement", "Steel", "Consumer Goods"], rows),
    "units_produced": np.random.randint(500, 20000, rows),
    "defect_rate": np.random.uniform(0.01, 0.15, rows),
    "production_cost": np.random.randint(10000, 200000, rows)
})

manufacturing.to_csv("data/manufacturing/factory_output.csv", index=False)


# ----------------------------
# FOOD & BEVERAGE
# ----------------------------

food = pd.DataFrame({
    "product_id": np.random.randint(100, 500, rows),
    "product_name": np.random.choice(["Soda", "Juice", "Beer", "Snacks"], rows),
    "region": np.random.choice(["North", "South", "East", "West"], rows),
    "units_sold": np.random.randint(50, 2000, rows),
    "revenue": np.random.randint(500, 50000, rows)
})

food.to_csv("data/food_beverage/sales.csv", index=False)


# ----------------------------
# LOGISTICS
# ----------------------------

logistics = pd.DataFrame({
    "warehouse_id": np.random.randint(1, 30, rows),
    "region": np.random.choice(["North", "South", "East", "West"], rows),
    "shipments_per_day": np.random.randint(20, 500, rows),
    "delivery_time_hours": np.random.uniform(2, 72, rows),
    "delayed_shipments": np.random.randint(0, 50, rows)
})

logistics.to_csv("data/logistics/shipments.csv", index=False)


print("All datasets successfully generated.")

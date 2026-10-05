"""Reproducible industry data and evidence computed from every row."""
import hashlib
import json
import numpy as np
import pandas as pd
from lab.config import ROOT

CATALOG = {
 "Oil & Gas": dict(file="oil_gas/production.csv", group="region", metric="production_barrels", risk="downtime_hours", icon=":material/oil_barrel:", description="Balance production, operating costs, and downtime.", unit="barrels"),
 "Healthcare": dict(file="healthcare/hospital_metrics.csv", group="department", metric="patients_per_day", risk="avg_wait_time_minutes", icon=":material/local_hospital:", description="Explore capacity, patient flow, and waiting times.", unit="patients"),
 "Manufacturing": dict(file="manufacturing/factory_output.csv", group="product", metric="units_produced", risk="defect_rate", icon=":material/precision_manufacturing:", description="Find the balance between output, cost, and quality.", unit="units"),
 "Food & Beverage": dict(file="food_beverage/sales.csv", group="region", metric="revenue", risk="units_sold", icon=":material/restaurant:", description="Understand regional sales and product performance.", unit="USD"),
 "Logistics": dict(file="logistics/shipments.csv", group="region", metric="shipments_per_day", risk="delivery_time_hours", icon=":material/local_shipping:", description="Improve delivery speed and warehouse performance.", unit="shipments")
}

def load_dataset(industry):
    return pd.read_csv(ROOT / "data" / CATALOG[industry]["file"])

def fingerprint(df):
    return hashlib.sha256(df.to_csv(index=False).encode()).hexdigest()[:16]

def label(column):
    return column.replace("_", " ").capitalize()

def aggregate(df, group, metric, operation="sum"):
    return df.groupby(group, dropna=False)[metric].agg(operation).sort_values(ascending=False)

def evidence(df, industry):
    spec = CATALOG[industry]
    numeric = df.select_dtypes(include="number")
    return json.dumps({
        "industry": industry, "rows": len(df), "columns": df.columns.tolist(),
        "missing": df.isna().sum().to_dict(),
        "statistics": numeric.describe().round(4).to_dict(),
        "group_totals": df.groupby(spec["group"])[numeric.columns].sum().round(4).to_dict(),
        "group_means": df.groupby(spec["group"])[numeric.columns].mean().round(4).to_dict(),
        "limitations": "Synthetic training data. Associations do not establish causes. ID columns are identifiers, not measures."
    }, default=str, allow_nan=False)

def generate_dataset(industry, rows=1000, seed=42):
    if industry not in CATALOG or not 100 <= rows <= 10000:
        raise ValueError("Choose a supported industry and 100–10,000 rows.")
    rng = np.random.default_rng(seed)
    region = rng.choice(["North", "South", "East", "West"], rows)
    efficiency = np.select([region == "North", region == "South", region == "East"], [1.12, .86, 1.04], default=.97)
    data = {"record_id": np.arange(1, rows+1), "date": pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0,365,rows),unit="D")}
    if industry == "Oil & Gas":
        downtime = np.round(rng.gamma(2,1.5,rows),1).clip(0,20)
        barrels = (rng.normal(1200,150,rows)*efficiency*(24-downtime)/24).clip(1).astype(int)
        data.update(well_id=rng.integers(1,101,rows),region=region,production_barrels=barrels,operational_cost=np.round(barrels*rng.uniform(28,42,rows)+downtime*450,2),downtime_hours=downtime)
    elif industry == "Healthcare":
        department = rng.choice(["Emergency","Outpatient","Surgery","Pediatrics"],rows)
        patients = rng.integers(30,280,rows)
        wait = (patients*.2+np.where(department=="Emergency",18,3)+rng.normal(0,6,rows)).clip(2)
        data.update(hospital_id=rng.integers(1,31,rows),department=department,patients_per_day=patients,avg_wait_time_minutes=np.round(wait,1),treatment_cost=np.round(patients*rng.uniform(70,140,rows),2))
    elif industry == "Manufacturing":
        units = (rng.integers(1000,10000,rows)*efficiency).astype(int)
        rate = np.round(rng.beta(2,55,rows),4)
        data.update(factory_id=rng.integers(1,21,rows),product=rng.choice(["Electronics","Consumer Goods","Industrial Parts"],rows),units_produced=units,defect_rate=rate,defective_units=np.rint(units*rate).astype(int),production_cost=np.round(units*rng.uniform(9,15,rows),2))
    elif industry == "Food & Beverage":
        names = rng.choice(["Coffee","Juice","Soda","Snack"],rows)
        price = pd.Series(names).map({"Coffee":5.,"Juice":4.,"Soda":2.,"Snack":3.}).to_numpy()
        units = (rng.integers(100,1800,rows)*efficiency).astype(int)
        data.update(product_id=pd.Series(names).map({"Coffee":1,"Juice":2,"Soda":3,"Snack":4}).to_numpy(),product_name=names,region=region,units_sold=units,unit_price=price,revenue=np.round(units*price,2))
    else:
        shipments = (rng.integers(80,600,rows)*efficiency).astype(int)
        hours = np.round(rng.gamma(5,4,rows)/efficiency,1)
        data.update(warehouse_id=rng.integers(1,31,rows),region=region,shipments_per_day=shipments,delivery_time_hours=hours,delayed_shipments=rng.binomial(shipments,np.clip(hours/180,.01,.65)))
    return pd.DataFrame(data).sort_values("date").reset_index(drop=True)

def dictionary(df):
    descriptions = {"record_id":"Unique synthetic observation","date":"Observation date in 2025","defect_rate":"Defective share, as a fraction (0–1)","revenue":"Sales value in USD","operational_cost":"Operating cost in USD","production_cost":"Production cost in USD","treatment_cost":"Treatment cost in USD","delayed_shipments":"Number of delayed shipments"}
    return pd.DataFrame([{"Column":c,"Type":str(df[c].dtype),"Meaning":descriptions.get(c,label(c))} for c in df.columns])

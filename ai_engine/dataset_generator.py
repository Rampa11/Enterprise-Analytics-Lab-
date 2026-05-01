import os
import pandas as pd
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------------------------------------------
# AI Dataset Structure Generator (SAFE VERSION)
# ---------------------------------------------------

def generate_dataset_structure(industry):

    prompt = f"""
You are a senior data engineer.

Create a realistic dataset structure for the {industry} industry.

Return ONLY column names.

Example:

customer_id
transaction_amount
branch
transaction_time
fraud_flag
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You design datasets."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        print("OpenAI error:", e)

        # 🔥 fallback dataset (ensures app never breaks)
        return """customer_id
transaction_amount
transaction_date
region
product_category
revenue"""


# ---------------------------------------------------
# COLUMN PARSER (NEW)
# ---------------------------------------------------

def parse_columns(text):
    columns = [col.strip() for col in text.split("\n") if col.strip()]

    # fallback if AI gives bad output
    if len(columns) < 3:
        columns = [
            "customer_id",
            "transaction_amount",
            "transaction_date",
            "region"
        ]

    return columns


# ---------------------------------------------------
# DATASET CREATOR (UNCHANGED CORE LOGIC)
# ---------------------------------------------------

def create_dataset(columns, rows=5000):

    data = {}

    for col in columns:

        col_lower = col.lower()

        if "id" in col_lower:
            data[col] = np.arange(rows)

        elif "amount" in col_lower or "revenue" in col_lower or "price" in col_lower:
            data[col] = np.random.randint(100, 10000, rows)

        elif "rate" in col_lower or "ratio" in col_lower:
            data[col] = np.random.uniform(0, 1, rows)

        elif "time" in col_lower or "date" in col_lower:
            data[col] = pd.date_range("2024-01-01", periods=rows)

        elif "region" in col_lower:
            data[col] = np.random.choice(
                ["North", "South", "East", "West"],
                rows
            )

        elif "category" in col_lower:
            data[col] = np.random.choice(
                ["A", "B", "C", "D"],
                rows
            )

        else:
            data[col] = np.random.randint(1, 100, rows)

    df = pd.DataFrame(data)

    return df
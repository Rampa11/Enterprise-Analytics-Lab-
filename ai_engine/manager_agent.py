import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------------------------
# Generate manager question (SAFE)
# ---------------------------------

def generate_manager_question(dataset_preview, industry, manager_role="operations_manager"):

    role_descriptions = {
        "operations_manager": "Operations Manager responsible for efficiency and logistics",
        "finance_manager": "Finance Manager responsible for revenue and profitability",
        "product_manager": "Product Manager responsible for product performance",
        "hr_manager": "HR Manager responsible for workforce performance",
        "project_manager": "Project Manager responsible for project delivery and execution"
    }

    role = role_descriptions.get(manager_role, "Business Manager")

    prompt = f"""
You are a {role} working in the {industry} industry.

You are speaking to a Data Analyst.

Based on the dataset preview below, ask ONE realistic business
question that requires analytical thinking and data investigation.

Dataset Preview:
{dataset_preview}

Examples of strong manager questions:

- Which region generates the highest revenue and why?
- Which warehouse contributes most to delivery delays?
- Which product line shows declining performance?
- What operational bottlenecks are affecting output?

Return ONLY the manager's question.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a corporate manager asking data analysts business questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Manager agent error:", e)

        # 🔥 fallback question (keeps app running)
        return "Which key factors in this dataset are driving performance, and where should we focus improvements?"
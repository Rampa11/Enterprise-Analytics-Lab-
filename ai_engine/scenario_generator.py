import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------------------------
# Business Scenario Generator (SAFE)
# ---------------------------------

def generate_business_scenario(industry, dataset_preview):

    prompt = f"""
You are a senior business consultant.

Create a realistic business analytics scenario for a data analyst.

Industry:
{industry}

Dataset Preview:
{dataset_preview}

Return STRICTLY in this format:

Scenario:
<Describe a realistic business problem>

Manager Request:
<What the manager wants investigated>

Goal:
<What insight the analyst should find>

Rules:
- Do NOT add extra sections
- Do NOT change the format
- Be clear and professional
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You create business analytics scenarios."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Scenario generator error:", e)

        # 🔥 fallback (keeps app running)
        return """Scenario:
A company is experiencing inconsistent performance across regions.

Manager Request:
Identify which regions are underperforming and determine possible causes.

Goal:
Find patterns in revenue, operations, or customer behavior that explain performance differences."""
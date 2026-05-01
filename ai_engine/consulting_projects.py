import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------------------------
# CONSULTING PROJECT GENERATOR (SAFE)
# ---------------------------------

def generate_consulting_project(dataset_preview, industry, manager_role):

    prompt = f"""
You are a senior {manager_role} in the {industry} industry.

You are assigning a data analyst a consulting-style analytics project.

Based on the dataset preview below, generate a realistic business
case study consisting of THREE steps.

Dataset Preview:
{dataset_preview}

Return STRICTLY in this format:

Project Brief:
<Explain the business situation>

Step 1:
<First analytical task>

Step 2:
<Second analytical task>

Step 3:
<Final strategic insight>

Rules:
- Do NOT add extra sections
- Do NOT change the format
- Keep it realistic and concise
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a business consultant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Consulting project error:", e)

        # 🔥 fallback (keeps app running)
        return """Project Brief:
A company is experiencing declining performance across key business areas.

Step 1:
Analyze the dataset to identify trends in performance metrics.

Step 2:
Determine which segments or regions are underperforming and why.

Step 3:
Provide strategic recommendations to improve overall performance."""
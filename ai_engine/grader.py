import os
from openai import OpenAI
from dotenv import load_dotenv
from .prompts import build_grading_prompt

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def grade_answer(question, dataset_info, user_answer):

    prompt = build_grading_prompt(question, dataset_info, user_answer)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a senior analytics evaluator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content

    except Exception as e:
        print("Grader error:", e)

        # 🔥 fallback response (VERY IMPORTANT)
        return """Score: N/A

⚠️ AI grading temporarily unavailable.

Please try again later or check your connection.

Tip:
- Ensure your answer includes structured reasoning
- Use data-driven insights
- Be clear and concise
"""
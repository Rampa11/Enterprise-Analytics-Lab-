def build_grading_prompt(question, dataset_info, user_answer):

    prompt = f"""
You are a senior data analytics manager.

A junior analyst was asked the following business question.

-------------------------
QUESTION:
{question}

DATASET CONTEXT:
{dataset_info}

ANALYST ANSWER:
{user_answer}
-------------------------

Evaluate the answer and return STRICTLY in the following format:

Score: <number between 0 and 100>

Feedback:
<Explain if the reasoning is correct, clear, and data-driven>

Correct Approach:
<Explain the correct analysis method clearly>

Rules:
- Do NOT add extra sections
- Do NOT change the format
- Be concise but professional
"""

    return prompt
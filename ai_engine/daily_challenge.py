import random
from datetime import date


daily_challenges = [
    "Find the region with the highest revenue.",
    "Identify the most delayed shipment zone.",
    "Determine the most productive manufacturing plant.",
    "Which hospital department treats the most patients?",
    "Which product generates the highest sales?"
]


def get_daily_challenge():
    # 🔥 use today's date as seed
    today = date.today()
    seed = int(today.strftime("%Y%m%d"))

    random.seed(seed)

    return random.choice(daily_challenges)
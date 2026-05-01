from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()

# ---------------------------------
# Supabase connection
# ---------------------------------

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)


# ---------------------------------
# Save score
# ---------------------------------

def save_score(user_email, score, challenge, industry, xp):

    if not user_email:
        return

    data = {
        "user_email": user_email,
        "score": score,
        "challenge": challenge,
        "industry": industry,
        "xp": xp,
        "date_completed": str(date.today())
    }

    try:
        supabase.table("leaderboard").insert(data).execute()
    except Exception as e:
        print("Leaderboard save error:", e)


# ---------------------------------
# Get top scores
# ---------------------------------

def get_top_scores():

    try:
        result = (
            supabase.table("leaderboard")
            .select("*")
            .order("score", desc=True)
            .limit(10)
            .execute()
        )

        return result.data if result.data else []

    except Exception as e:
        print("Leaderboard fetch error:", e)
        return []


# ---------------------------------
# Get user history
# ---------------------------------

def get_user_scores(user_email):

    if not user_email:
        return []

    try:
        result = (
            supabase.table("leaderboard")
            .select("*")
            .eq("user_email", user_email)
            .order("date_completed", desc=True)  # 🔥 fixed consistency
            .execute()
        )

        return result.data if result.data else []

    except Exception as e:
        print("User scores fetch error:", e)
        return []
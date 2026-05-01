from auth import supabase

def upsert_user(email, user_id):
    supabase.table("users_profile").upsert({
        "id": user_id,
        "email": email
    }).execute()


def upgrade_to_premium(user_id):
    supabase.table("users_profile").update({
        "plan": "premium"
    }).eq("id", user_id).execute()


def add_credits(user_id, amount=2):
    user = supabase.table("users_profile").select("*").eq("id", user_id).execute().data[0]

    new_credits = user["credits"] + amount

    supabase.table("users_profile").update({
        "credits": new_credits
    }).eq("id", user_id).execute()


def use_credit(user_id):

    res = supabase.table("users_profile") \
        .select("credits") \
        .eq("id", user_id) \
        .execute()

    credits = res.data[0]["credits"]

    if credits <= 0:
        return False

    supabase.table("users_profile").update({
        "credits": credits - 1
    }).eq("id", user_id).execute()

    return True
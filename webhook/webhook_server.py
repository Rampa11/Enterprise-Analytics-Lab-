from fastapi import FastAPI, Request, HTTPException
import stripe
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# ---------------------------------
# CONFIG
# ---------------------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# ---------------------------------
# WEBHOOK ENDPOINT
# ---------------------------------
@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # ---------------------------------
    # HANDLE PAYMENT SUCCESS
    # ---------------------------------
    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        user_id = session.get("client_reference_id")
        plan_type = session.get("metadata", {}).get("plan")

        if not user_id:
            return {"status": "no user_id"}

        # ---------------------------------
        # PREMIUM
        # ---------------------------------
        if plan_type == "premium":
            supabase.table("users_profile") \
                .update({"plan": "premium"}) \
                .eq("id", user_id) \
                .execute()

        # ---------------------------------
        # ANSWER PACK
        # ---------------------------------
        elif plan_type == "answers":

            user = supabase.table("users_profile") \
                .select("credits") \
                .eq("id", user_id) \
                .execute()

            if user.data:
                current = user.data[0]["credits"]

                supabase.table("users_profile") \
                    .update({"credits": current + 2}) \
                    .eq("id", user_id) \
                    .execute()

    return {"status": "success"}
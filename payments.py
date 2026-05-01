import stripe
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(plan_type, email):

    DOMAIN = os.getenv("APP_URL", "http://localhost:8501")

    if plan_type == "answers":
        price_id = "price_1TCFglBoWdH4kCN5z628WPt7"
        mode = "payment"

    elif plan_type == "premium":
        price_id = "price_1TCFdZBoWdH4kCN5DpwNtqDM"
        mode = "subscription"

    else:
        return None

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode=mode,
            customer_email=email,
            success_url=f"{DOMAIN}/?payment_success={plan_type}",
            cancel_url=f"{DOMAIN}",
        )

        return session.url

    except Exception as e:
        import streamlit as st
        st.error(f"Stripe error: {e}")
        return None
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_checkout_session(plan_type, email, user_id=None):
    """
    Creates a Stripe checkout session.

    plan_type: "answers" or "premium"
    email: user email
    user_id: Supabase user ID (IMPORTANT for webhook)
    """

    DOMAIN = os.getenv("APP_URL", "http://localhost:8501")

    # ---------------------------------
    # PLAN CONFIG
    # ---------------------------------
    if plan_type == "answers":
        price_id = "price_1TCFglBoWdH4kCN5z628WPt7"
        mode = "payment"

    elif plan_type == "premium":
        price_id = "price_1TCFdZBoWdH4kCN5DpwNtqDM"
        mode = "subscription"

    else:
        return None

    # ---------------------------------
    # CREATE CHECKOUT SESSION
    # ---------------------------------
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode=mode,
        
            customer_email=email,
            client_reference_id=user_id,  # better than email

            metadata={
                "plan": plan_type,
                "user_id": user_id if user_id else "",
                "email": email
            },

            success_url=f"{DOMAIN}/?payment_success={plan_type}",
            cancel_url=f"{DOMAIN}",
        )
        if "payment_success" in st.query_params:
            st.success("Payment successful! 🎉")
            st.rerun()

        return session.url

    except Exception as e:
        import streamlit as st
        st.error(f"Stripe error: {e}")
        return None
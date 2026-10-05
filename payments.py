"""Checkout redirects never modify access. Only signed webhooks do."""
import stripe
from auth import verify_user
from lab.config import setting

def available(plan):
    price = "STRIPE_ANSWERS_PRICE_ID" if plan=="answers" else "STRIPE_PREMIUM_PRICE_ID"
    return bool(setting("STRIPE_SECRET_KEY") and setting(price) and setting("BILLING_ENABLED")=="true")

def create_checkout_session(plan_type, email=None, user_id=None):
    if plan_type not in ("answers","premium") or not available(plan_type):
        raise RuntimeError("Checkout is not available yet.")
    user = verify_user()
    stripe.api_key = setting("STRIPE_SECRET_KEY")
    price = setting("STRIPE_ANSWERS_PRICE_ID" if plan_type=="answers" else "STRIPE_PREMIUM_PRICE_ID")
    domain = setting("APP_URL","http://localhost:8501").rstrip("/")
    metadata = {"plan":plan_type,"user_id":user.id}
    args = dict(line_items=[{"price":price,"quantity":1}],mode="payment" if plan_type=="answers" else "subscription",
        customer_email=user.email,client_reference_id=user.id,metadata=metadata,
        success_url=domain+"/?checkout=returned",cancel_url=domain+"/Pricing")
    if plan_type=="premium":
        args["subscription_data"]={"metadata":metadata}
    return stripe.checkout.Session.create(**args).url


def billing_portal():
    from lab.storage import admin_client
    user = verify_user()
    admin = admin_client()
    if admin is None:
        raise RuntimeError("Billing unavailable")
    rows = admin.table("lab_profiles").select("stripe_customer_id").eq("user_id",user.id).execute().data
    if not rows or not rows[0].get("stripe_customer_id"):
        raise RuntimeError("No billing account")
    stripe.api_key = setting("STRIPE_SECRET_KEY")
    return stripe.billing_portal.Session.create(customer=rows[0]["stripe_customer_id"],return_url=setting("APP_URL","http://localhost:8501")+"/Pricing").url

"""Signed Stripe events; atomic, idempotent entitlement updates."""
import os
from datetime import datetime,timezone
import stripe
from dotenv import load_dotenv
from fastapi import FastAPI,Request,HTTPException
from supabase import create_client
load_dotenv()
app=FastAPI()

def apply_event(event,db):
    kind=event["type"]
    obj=event["data"]["object"]
    args=dict(p_event_key=event["id"],p_user_id=None,p_credits=0,p_plan=None,p_until=None,p_customer=None,p_subscription=None,p_version=event["created"])
    if kind in ("checkout.session.completed","checkout.session.async_payment_succeeded"):
        session=stripe.checkout.Session.retrieve(obj["id"],expand=["line_items"])
        if session.get("payment_status")!="paid": return
        plan=session.get("metadata",{}).get("plan")
        args["p_user_id"]=session.get("client_reference_id")
        args["p_customer"]=session.get("customer")
        if plan=="answers":
            items=session["line_items"]["data"]
            expected=os.environ.get("STRIPE_ANSWERS_PRICE_ID")
            if len(items)!=1 or items[0]["price"]["id"]!=expected or items[0]["quantity"]!=1:
                raise ValueError("Unexpected checkout price")
            args.update(p_event_key="checkout:"+session["id"],p_credits=2)
        elif plan=="premium":
            return  # Subscription lifecycle and invoices are authoritative.
        else: return
    elif kind in ("customer.subscription.created","customer.subscription.updated","customer.subscription.deleted","invoice.paid","invoice.payment_failed"):
        subscription_id=obj["id"] if kind.startswith("customer.subscription.") else obj.get("subscription") or obj.get("parent",{}).get("subscription_details",{}).get("subscription")
        if not subscription_id: return
        sub=stripe.Subscription.retrieve(subscription_id)
        args["p_user_id"]=sub.get("metadata",{}).get("user_id")
        items=sub["items"]["data"]
        expected=os.environ.get("STRIPE_PREMIUM_PRICE_ID")
        if not items or not any(item["price"]["id"]==expected for item in items): return
        active=sub["status"] in ("active","trialing")
        end=sub.get("current_period_end") or max(item.get("current_period_end",0) for item in items)
        if active and not end: raise ValueError("Missing subscription period")
        args.update(p_plan="premium" if active else "free",p_until=datetime.fromtimestamp(end,timezone.utc).isoformat() if end else None,
                    p_customer=sub.get("customer"),p_subscription=sub["id"])
    else: return
    if not args["p_user_id"]: raise ValueError("Missing user reference")
    db.rpc("lab_apply_billing",args).execute()

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/webhook")
async def webhook(request:Request):
    required=["STRIPE_SECRET_KEY","STRIPE_WEBHOOK_SECRET","SUPABASE_URL","SUPABASE_SERVICE_ROLE_KEY"]
    if not all(os.getenv(key) for key in required):
        raise HTTPException(503,"Webhook configuration incomplete")
    stripe.api_key=os.environ["STRIPE_SECRET_KEY"]
    try:
        event=stripe.Webhook.construct_event(await request.body(),request.headers.get("stripe-signature"),os.environ["STRIPE_WEBHOOK_SECRET"])
    except (ValueError,stripe.SignatureVerificationError):
        raise HTTPException(400,"Invalid webhook signature") from None
    try:
        db=create_client(os.environ["SUPABASE_URL"],os.environ["SUPABASE_SERVICE_ROLE_KEY"])
        apply_event(event,db)
    except Exception:
        # Non-2xx causes Stripe to retry transient delivery failures.
        raise HTTPException(503,"Event processing unavailable") from None
    return {"received":True}

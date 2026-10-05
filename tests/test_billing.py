import hashlib
import hmac
import json
import time
from types import SimpleNamespace
from fastapi.testclient import TestClient
import pytest
import payments
from webhook import webhook_server as wh

class DB:
    def __init__(self): self.calls=[]
    def rpc(self,name,args):
        self.calls.append((name,args))
        return SimpleNamespace(execute=lambda:None)

def test_answer_credit_uses_session_id_for_dedup(monkeypatch):
    monkeypatch.setenv("STRIPE_ANSWERS_PRICE_ID","price_pack")
    session=dict(id="cs_test",payment_status="paid",metadata={"plan":"answers"},client_reference_id="user",customer="cus",line_items={"data":[{"price":{"id":"price_pack"},"quantity":1}]})
    monkeypatch.setattr(wh.stripe.checkout.Session,"retrieve",lambda *a,**kw:session)
    db=DB()
    for kind in ["checkout.session.completed","checkout.session.async_payment_succeeded"]:
        wh.apply_event({"type":kind,"id":kind,"created":10,"data":{"object":{"id":"cs_test"}}},db)
    assert all(args["p_event_key"]=="checkout:cs_test" and args["p_credits"]==2 for _,args in db.calls)
    session["payment_status"]="unpaid"
    wh.apply_event({"type":"checkout.session.completed","id":"later","created":11,"data":{"object":{"id":"cs_test"}}},db)
    assert len(db.calls)==2

def test_wrong_price_rejected(monkeypatch):
    monkeypatch.setenv("STRIPE_ANSWERS_PRICE_ID","expected")
    session=dict(id="cs",payment_status="paid",metadata={"plan":"answers"},client_reference_id="user",line_items={"data":[{"price":{"id":"wrong"},"quantity":1}]})
    monkeypatch.setattr(wh.stripe.checkout.Session,"retrieve",lambda *a,**kw:session)
    with pytest.raises(ValueError): wh.apply_event({"type":"checkout.session.completed","id":"evt","created":1,"data":{"object":{"id":"cs"}}},DB())

def test_subscription_expiry_and_cancellation(monkeypatch):
    monkeypatch.setenv("STRIPE_PREMIUM_PRICE_ID","premium")
    sub=dict(id="sub",status="active",metadata={"user_id":"user"},customer="cus",items={"data":[{"price":{"id":"premium"},"current_period_end":2000000000}]})
    monkeypatch.setattr(wh.stripe.Subscription,"retrieve",lambda *a,**kw:sub)
    db=DB()
    event={"type":"customer.subscription.updated","id":"evt","created":10,"data":{"object":{"id":"sub"}}}
    wh.apply_event(event,db)
    assert db.calls[-1][1]["p_plan"]=="premium"
    assert db.calls[-1][1]["p_until"] is not None
    sub["status"]="canceled"
    wh.apply_event(event,db)
    assert db.calls[-1][1]["p_plan"]=="free"

def test_webhook_rejects_invalid_signature(monkeypatch):
    for key in ["STRIPE_SECRET_KEY","STRIPE_WEBHOOK_SECRET","SUPABASE_URL","SUPABASE_SERVICE_ROLE_KEY"]: monkeypatch.setenv(key,"test")
    client=TestClient(wh.app)
    assert client.post("/webhook",content=b"{}",headers={"stripe-signature":"invalid"}).status_code==400
    secret="whsec_test"
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET",secret)
    monkeypatch.setattr(wh,"create_client",lambda *a:DB())
    payload=json.dumps({"id":"evt","type":"unhandled","created":1,"data":{"object":{}}})
    ts=int(time.time())
    sig=hmac.new(secret.encode(),f"{ts}.{payload}".encode(),hashlib.sha256).hexdigest()
    response=client.post("/webhook",content=payload,headers={"stripe-signature":f"t={ts},v1={sig}"})
    assert response.status_code==200

def test_checkout_requires_verified_account(monkeypatch):
    monkeypatch.setattr(payments,"available",lambda p:True)
    def expired(): raise RuntimeError("expired")
    monkeypatch.setattr(payments,"verify_user",expired)
    with pytest.raises(RuntimeError,match="expired"): payments.create_checkout_session("premium","spoofed@example.com","other")

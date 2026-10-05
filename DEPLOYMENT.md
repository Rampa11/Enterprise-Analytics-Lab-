# Deployment checklist

## Streamlit Cloud

Keep dashboard.py as the entry point and Python 3.11 or 3.12. The redesign uses the existing Streamlit host and repository layout.

1. Deploy the reviewed branch after completing the database setup below.
2. Configure the server secrets listed in .env.example.
3. Initially leave BILLING_ENABLED=false.
4. Smoke-test all navigation pages, guest practice, generated datasets, and the daily challenge.
5. Sign up with a test account, confirm email, sign in, submit a challenge, sign out, and verify persistence after a fresh sign-in.

## Supabase

Run sql/platform_setup.sql in the SQL editor. It creates lab_profiles, lab_attempts, lab_unlocks, lab_billing_events, lab_ai_usage, and five restricted RPCs. It does not replace existing analytics tables.

Verify:
- Anonymous users cannot read any learning tables.
- An authenticated user can read only their own profile and unlocks.
- Neither anon nor authenticated can execute score, credit, billing, or leaderboard RPCs.
- Full attempt answers are accessible only through the app server.
- Retrying the same challenge keeps one row and the best score.
- Unlocking twice spends only one credit, including concurrent requests.

The service-role key belongs only in server environments. Never commit it, expose it in client JavaScript, or log it.

Before charging existing customers, reconcile legacy users_profile credits/subscriptions with lab_profiles. Keep the old tables as a reference; do not delete legacy records. Stripe remains the source of truth for subscription state. This release deliberately does not infer paid access from a URL or unverified historical leaderboard row.

## Stripe and Render

Create or verify the existing prices: a USD 5 one-time answer pack (2 credits), and USD 20/month Premium. Set their IDs in STRIPE_ANSWERS_PRICE_ID and STRIPE_PREMIUM_PRICE_ID in both the app and webhook environments. The advertised prices must match the configured Stripe prices.

Render service:
- Root directory: webhook
- Build command: pip install -r requirements.txt
- Start command: uvicorn webhook_server:app --host 0.0.0.0 --port $PORT
- Health check: /health
- Environment: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, both price IDs.

Register /webhook in Stripe for:
- checkout.session.completed
- checkout.session.async_payment_succeeded
- customer.subscription.created
- customer.subscription.updated
- customer.subscription.deleted
- invoice.paid
- invoice.payment_failed

Configure Stripe's customer billing portal to allow subscription cancellation. The app includes a portal link for premium accounts.

Use Stripe test mode before enabling real checkout. Verify:
1. Answer pack grants exactly 2 credits.
2. Replaying an event and delivering the async event for the same Checkout session adds nothing further.
3. A wrong price or unpaid session grants nothing.
4. A subscription activates, renews, becomes past due, and cancels correctly.
5. Refreshing a return URL never grants access.
6. Failed webhook processing returns 503 so Stripe retries.
7. Credit consumption is atomic and repeat unlocks are free.
8. An account can open only its own customer portal.

Enable BILLING_ENABLED=true only after these checks and legacy entitlement reconciliation. Refund/dispute policy and support contact must be decided operationally before taking live payments; this release does not automatically claw back spent credits.

## Release status

Local offline tests cover the learning flows and mocked service boundaries. The database setup and real payment lifecycle must be verified against the deployment environment. The source alone does not provision or publish external services.

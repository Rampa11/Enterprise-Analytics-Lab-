# Enterprise Analytics Lab

A practical analytics learning workspace built with Streamlit. Choose an industry, inspect a full dataset, solve a business question, and turn the result into a recommendation.

## Run

Use Python 3.11 or 3.12.

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard.py
```

The app works without credentials in guest mode. Guest progress lives only in the Streamlit session and is lost when that session ends. Set LAB_OFFLINE=1 to explicitly disable every external service during demos and tests.

## Learning experience

- Five industry datasets: oil and gas, healthcare, manufacturing, food and beverage, logistics.
- Three dataset-specific challenges per industry, with answer keys computed from all observations.
- Filterable tables, chart exploration, data dictionaries, CSV downloads.
- Numerical scoring: 50 points for identifying a leading segment, 50 for the correct aggregate. Numeric tolerance is 0.5% or 0.01 absolute. Written reasoning is not automatically scored by this numerical check.
- Daily UTC challenges with saved results and best-attempt XP.
- Three-step manager projects with optional structured AI grading. Missing or invalid AI responses never award scores or XP.
- Reproducible synthetic dataset generation. Generated datasets can be used immediately in the practice lab.
- Progress history, exportable analysis records, levels, streaks, badges, and pseudonymous rankings.
- Free scores, paid worked answers, permanent credit unlocks, and premium detailed coaching.

## Accounts and persistence

Copy .env.example to .env locally, or set the same keys in Streamlit Cloud Secrets.

1. Use the existing Supabase project; configure SUPABASE_URL and SUPABASE_ANON_KEY.
2. Run sql/platform_setup.sql in its SQL editor. This is additive and leaves the legacy analytics tables intact.
3. Add SUPABASE_SERVICE_ROLE_KEY to the app's server secrets and webhook environment only.
4. Enable email/password authentication and email confirmation in Supabase.
5. Sign in; the app creates a pseudonymous learning profile. Public rankings never show emails.
6. Test an answer, reload the account, and verify the saved result.

All score and entitlement mutations are server-owned and require a verified account. Database RPCs are restricted to service_role. Full answer JSON is not exposed to the authenticated Data API. Each Streamlit session gets its own auth client.

Legacy users can continue signing in. Previous users_profile credits, subscriptions, and leaderboard entries are **not automatically migrated**. Review and migrate those before enabling paid checkout. Old leaderboard rows cannot safely be treated as new verified challenge results because they lack stable dataset/challenge IDs.

## AI

OPENAI_API_KEY enables structured reviews and new manager briefs for signed-in accounts. An atomic daily allowance permits 5 AI requests on Free and 100 on Premium. Failed provider requests may consume an AI request allowance, but never an answer credit. OPENAI_MODEL defaults to the project's original gpt-4o-mini. Reviews receive column statistics and grouped totals/means computed from all rows, not a five-row sample. These summaries do not support arbitrary causal claims or every possible analysis; feedback explicitly treats those as limitations.

AI assessments are advisory and may be imperfect. Failures preserve the draft and offer a retry. Numerical checks remain available independently.

## Billing

See DEPLOYMENT.md. No browser URL grants credits or premium access. Stripe signature verification, expected price checks, and atomic database updates are required. Credits deduplicate by Checkout session; subscription lifecycle events update access and expiry.

## Tests

```sh
pip install -r requirements-dev.txt
python -m pytest tests -q
```

The suite runs offline with mocked third-party services. Real Supabase and Stripe integration checks are separate deployment requirements.

## Original project

Created by Akpor Unukogbon (The Cardinal Way).

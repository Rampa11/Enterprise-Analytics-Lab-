import streamlit as st
import webbrowser
from payments import create_checkout_session

st.set_page_config(page_title="Pricing", layout="wide")

st.title("💳 Pricing Plans")
st.write("Choose a plan that fits your growth.")

st.markdown("---")

# Get user email (for Stripe + future Supabase)
email = st.session_state.get("user")

# Create columns
col1, col2, col3 = st.columns(3)

# ---------------------------------
# FREE PLAN
# ---------------------------------
with col1:
    st.subheader("🆓 Free")

    st.write("""
    - Limited practice questions  
    - Score only (no answers)  
    - Limited AI access  
    """)

    st.info("Current Plan")

# ---------------------------------
# ANSWER PACK
# ---------------------------------
with col2:
    st.subheader("💡 $5 — Answer Pack")

    st.write("""
    - Unlock **2 full answers**  
    - One-time purchase  
    """)

    if st.button("Buy Answer Pack"):

        if not email:
            st.error("Please login first")
        else:
            url = create_checkout_session("answers", email)

            if url:
                st.link_button("👉 Pay Now", url)
            else:
                st.error("⚠️ Payment system not ready yet.")

# ---------------------------------
# PREMIUM PLAN
# ---------------------------------
with col3:
    st.subheader("🚀 $20/month — Premium")

    st.write("""
    - Unlimited practice  
    - Full AI feedback  
    - All industries  
    """)

    if st.button("Go Premium"):

        if not email:
            st.error("Please login first")
        else:
            url = create_checkout_session("premium", email)

            if url:
                webbrowser.open(url)
            else:
                st.error("⚠️ Payment system not ready yet.")

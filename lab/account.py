import streamlit as st
from auth import current_user,get_client,sign_in,sign_out
from lab import storage
from lab.ui import heading
from payments import available,create_checkout_session

def account():
    heading("Account","Your place in the lab.","Save your progress and continue building your skills.")
    if current_user():
        st.success("Signed in as "+current_user()["email"])
        if st.button("Sign out"):
            sign_out()
            st.rerun()
        return
    if not get_client():
        st.info("Account services are not connected in this preview. Explore every industry and try numerical challenges as a guest.")
        st.page_link("pages/Practice_Lab.py",label="Continue as a guest",icon=":material/arrow_forward:")
        return
    login,signup=st.tabs(["Sign in","Create an account"])
    with login,st.form("login"):
        email=st.text_input("Email",max_chars=254)
        password=st.text_input("Password",type="password")
        submitted=st.form_submit_button("Sign in",type="primary")
    if submitted:
        try:
            sign_in(email,password)
            try: storage.ensure_profile()
            except Exception: st.session_state["account_notice"]="Signed in, but saved progress needs configuration."
            st.rerun()
        except Exception:
            st.error("Could not sign in. Check your email, password, and email confirmation.")
    with signup,st.form("signup"):
        name=st.text_input("Your name",max_chars=80)
        new_email=st.text_input("Email address",max_chars=254)
        new_password=st.text_input("Choose a password",type="password",help="Use at least 8 characters.")
        create=st.form_submit_button("Create account")
    if create:
        if not name.strip() or "@" not in new_email or len(new_password)<8:
            st.warning("Enter your name, a valid email, and a password of at least 8 characters.")
        else:
            try:
                get_client().auth.sign_up({"email":new_email.strip(),"password":new_password,"options":{"data":{"full_name":name.strip()}}})
                st.success("Check your email for confirmation, then return to sign in.")
            except Exception:
                st.error("Account creation is unavailable. Check the details or try again later.")
    st.page_link("pages/Practice_Lab.py",label="Try a guest challenge first",icon=":material/arrow_forward:")

def pricing():
    heading("Membership / Learning plans","Invest in your next insight.","Practice for free. Add worked answers and deeper coaching when you need them.")
    plans=[
        ("Explorer","Free","Build a habit, one question at a time.",["All five industries","Numerical answer checks","Daily challenges and dataset downloads","5 AI requests per day when connected"],None),
        ("Answer pack","$5","Guidance, right when you need it.",["Two permanent challenge unlocks","Worked answers and full feedback","One-time payment"],"answers"),
        ("Premium","$20 / month","Go further with every analysis.",["All worked answers","Detailed AI feedback when available","AI coaching on your reasoning","100 AI requests per day when connected"],"premium")]
    for col,(title,price,desc,features,plan) in zip(st.columns(3),plans):
        with col,st.container(border=True):
            st.caption(title.upper())
            st.subheader(price)
            st.write(desc)
            for feature in features: st.write("✓ "+feature)
            if not plan:
                st.page_link("pages/Practice_Lab.py",label="Start practicing",icon=":material/arrow_forward:")
            elif not current_user():
                st.page_link("pages/Login.py",label="Sign in to upgrade",icon=":material/login:")
            elif not available(plan):
                st.button("Checkout coming soon",disabled=True,key="disabled_"+plan)
            elif st.button("Choose "+title,type="primary",key="buy_"+plan):
                try: st.session_state["checkout_"+plan]=create_checkout_session(plan)
                except Exception: st.error("Could not open checkout. Please try again shortly.")
            if st.session_state.get("checkout_"+str(plan)):
                st.link_button("Continue to secure checkout",st.session_state["checkout_"+plan])
    if current_user():
        p=storage.profile()
        st.info(f"Your plan: {p['plan'].capitalize()} · {p['credits']} credits")
        if st.button("Refresh payment status"): st.rerun()
        if p["plan"]=="premium":
            if st.button("Manage or cancel subscription",disabled=not available("premium")):
                try:
                    from payments import billing_portal
                    st.link_button("Open billing portal",billing_portal())
                except Exception: st.error("The billing portal is unavailable. Contact the site owner.")
    st.caption("Access updates after payment verification. Failed AI reviews never award scores or spend answer credits.")

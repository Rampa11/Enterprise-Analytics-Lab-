import streamlit as st
import os
from db import upgrade_to_premium, add_credits
import streamlit as st
import base64

# ---------------------------------
# GLOBAL STYLES (SIDEBAR + UI)
# ---------------------------------
st.markdown("""
<style>

/* Sidebar background (robust selector) */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: white !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    border: none;
}

/* Hover */
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #1d4ed8;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------
# BACKGROUND FUNCTION (ONLY ONCE)
# ---------------------------------
def set_bg(image_file):
    with open(image_file, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: 
            linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)),
            url("data:image/png;base64,{data}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)


# APPLY BACKGROUND
set_bg("assets/dashboard4.png")

def set_bg(image_file):
    with open(image_file, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)
    set_bg("assets/dashboard4.png")

def set_bg(image_file):
    import base64

    with open(image_file, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: 
            linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)),
            url("data:image/png;base64,{data}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg("assets/dashboard4.png")
# ---------------------------------
# ENV DETECTION
# ---------------------------------
LOCAL = os.path.exists(".env")

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(
    page_title="Enterprise Analytics Lab",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------
# INIT STATE
# ---------------------------------
if "tour_step" not in st.session_state:
    st.session_state.tour_step = 0

if "plan" not in st.session_state:
    st.session_state.plan = "free"

if "answer_credits" not in st.session_state:
    st.session_state.answer_credits = 0

# ---------------------------------
# HANDLE STRIPE SUCCESS
# ---------------------------------
params = st.query_params

if "payment_success" in params:

    plan_type = params["payment_success"]
    user_id = st.session_state.get("user_id")

    if not user_id:
        st.error("User not found. Please login again.")
    else:
        if plan_type == "premium":
            upgrade_to_premium(user_id)
            st.session_state.plan = "premium"
            st.success("🎉 You are now a Premium user!")
            st.session_state.show_upgrade_popup = False

        elif plan_type == "answers":
            add_credits(user_id, 2)
            st.session_state.answer_credits += 2
            st.success("🎉 You received 2 answer credits!")
            st.session_state.show_upgrade_popup = False

        st.query_params.clear()

# ---------------------------------
# LANDING PAGE (NOT LOGGED IN)
# ---------------------------------
if "user" not in st.session_state:

    
    col1, col2 = st.columns([1, 3])

    with col1:
        st.image("assets/kardinal_logo.png", width=130)

    with col2:
        st.title("Enterprise Analytics Lab")
        st.caption("Learn Data Analytics by Solving Real Business Problems")

    st.markdown("---")

    
    st.markdown("""
    <div style="
    background: rgba(0,0,0,0.5);
    backdrop-filter: blur(10px);
    padding: 30px;
    border-radius: 15px;
    color: white;
    max-width: 800px;
    ">
    """, unsafe_allow_html=True)

    
    tab = st.radio(
        "Explore",
        ["🌍 Vision", "🎯 Mission", "📈 Goals"],
        horizontal=True
    )

    
    if "Vision" in tab:
        st.markdown("### 🌍 Vision")
        st.write(
            "Build a global platform where anyone learns analytics through real business problems."
        )

    elif "Mission" in tab:
        st.markdown("### 🎯 Mission")
        st.write(
            "Bridge the gap between theory and real-world analytics using AI-powered simulations."
        )

    elif "Goals" in tab:
        st.markdown("""
### 📈 Goals  
- Train world-class analysts  
- Simulate real business challenges  
- Enable data-driven decision making  
""")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(" ")

    # VALUE SECTION
    st.markdown("""
### 🚀 Learn Faster by Doing — Not Watching

> “The best way to learn data analytics is not by watching tutorials,
but by solving real business problems.”  
**— The Cardinal Way**
""")

    st.write("""
• Work with real datasets  
• Solve AI business challenges  
• Get instant feedback  
• Build real skills  
""")

    st.markdown("---")


    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Start Learning", use_container_width=True):
            st.switch_page("pages/0_Login.py")

    with col2:
        if st.button("💳 View Pricing", use_container_width=True):
            st.switch_page("pages/7_Pricing.py")  # or "7_Pricing" if that's your page name

    st.info("You are using the Free version. Login to unlock more features.")

    st.stop()

# ---------------------------------
# LOAD USER DATA FROM SUPABASE
# ---------------------------------
if "data_loaded" not in st.session_state:

    from auth import supabase

    res = supabase.table("users_profile") \
        .select("*") \
        .eq("id", st.session_state["user_id"]) \
        .execute()

    if res.data:
        st.session_state.plan = res.data[0]["plan"]
        st.session_state.answer_credits = res.data[0]["credits"]

    st.session_state.data_loaded = True

# ---------------------------------
# DASHBOARD (LOGGED IN)
# ---------------------------------
st.sidebar.markdown("## 👤 Account")

st.sidebar.write(f"User: {st.session_state.get('user', 'Guest')}")
st.sidebar.write(f"Plan: {st.session_state.get('plan', 'free')}")
st.sidebar.write(f"Credits: {st.session_state.get('answer_credits', 0)}")

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout"):
    st.session_state.pop("user", None)
    st.session_state.pop("plan", None)
    st.session_state.pop("answer_credits", None)

    st.rerun()

st.title("📊 ENTERPRISE ANALYTICS LAB")
st.subheader("AI-Powered Business Intelligence Platform")

if LOCAL:
    st.success("🟢 Connected to PostgreSQL (Local Mode)")
    st.markdown("---")

st.markdown("## 🚀 Enterprise Analytics Lab")

tab = st.radio(
    "",
    ["Vision", "Mission", "Goals"],
    horizontal=True
)

if tab == "Vision":
    st.info("🌍 Build real-world data analytics skills through business problem solving.")

elif tab == "Mission":
    st.info("🎯 Bridge theory and practice using AI-powered analytics training.")

elif tab == "Goals":
    st.info("📈 Develop top analysts, simulate real business challenges, and drive impact.")
else:
    st.info("🟡 Running in Demo Mode (CSV Data)")

st.sidebar.title("Enterprise Analytics Lab")
st.sidebar.warning("🚀 Upgrade to Premium in Pricing")

# ---------------------------------
# TOUR STEPS
# ---------------------------------
def get_tour_steps(plan):

    steps = [
        {
            "title": "👋 Welcome",
            "content": "Learn data analytics by solving real business problems."
        },
        {
            "title": "📊 Practice Lab",
            "content": "Solve real questions and get AI grading."
        }
    ]

    if plan == "free":
        steps.append({
            "title": "💡 Limited Access",
            "content": "Answers are locked. Upgrade to unlock."
        })

    elif plan == "premium":
        steps.extend([
            {
                "title": "🤖 AI Business Manager",
                "content": "Full AI challenge access."
            },
            {
                "title": "💎 Full Access",
                "content": "Unlimited answers and feedback."
            }
        ])

    return steps

# ---------------------------------
# TOUR UI
# ---------------------------------
def show_tour():

    plan = st.session_state.get("plan", "free")
    steps = get_tour_steps(plan)
    step = st.session_state.get("tour_step", 0)

    st.markdown("---")
    st.markdown(f"### 🚀 Product Tour ({step + 1}/{len(steps)})")

    st.info(steps[step]["title"])
    st.write(steps[step]["content"])

    col1, col2 = st.columns(2)

    with col1:
        if step > 0 and st.button("⬅ Back"):
            st.session_state.tour_step -= 1
            st.rerun()

    with col2:
        if step < len(steps) - 1:
            if st.button("Next ➡"):
                st.session_state.tour_step += 1
                st.rerun()
        else:
            if st.button("Finish Tour"):
                st.session_state.show_tour = False
                st.rerun()

    #    CONVERSION TRIGGER
    if plan == "free" and step == len(steps) - 1:
        st.warning("🔒 Unlock full answers with Premium or Answer Pack.")
        if st.button("🚀 Upgrade Now"):
            st.switch_page("pages/7_Pricing.py")

# ---------------------------------
# CALL TOUR
# ---------------------------------
if st.session_state.get("show_tour"):
    show_tour()

# ---------------------------------
# DASHBOARD CONTENT
# ---------------------------------
st.header("Welcome")

st.write(f"User: {st.session_state.user}")
st.write(f"Plan: {st.session_state.plan}")
st.write(f"Credits: {st.session_state.answer_credits}")
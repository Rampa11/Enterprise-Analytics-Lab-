import streamlit as st
from data_loader import load_industry_data
from ai_engine.grader import grade_answer
from ai_engine.leaderboard import save_score
from ai_engine.xp_system import calculate_xp

st.title("Data Analyst Practice Lab")

# ---------------------------------
# LOAD DATA
# ---------------------------------

df = load_industry_data()

if df is None:
    st.warning("Please select an industry first")
    st.stop()

st.subheader("Dataset Preview")
st.dataframe(df.head())

# ---------------------------------
# USER STATE
# ---------------------------------

plan = st.session_state.get("plan", "free")
credits = st.session_state.get("answer_credits", 0)

# ---------------------------------
# QUESTIONS
# ---------------------------------

questions = [
    {"q": "Which region has the highest operational activity?"},
    {"q": "Which unit generates the highest revenue?"},
    {"q": "Which segment shows the largest delays?"},
    {"q": "Which category has the highest output?"}
]

# ---------------------------------
# LIMIT ACCESS
# ---------------------------------

if plan == "visitor":
    visible_questions = questions[:1]

elif plan == "registered":
    visible_questions = questions[:3]

else:
    visible_questions = questions

# ---------------------------------
# MAIN LOOP
# ---------------------------------

for i, q in enumerate(visible_questions):

    st.subheader(f"Question {i+1}")
    st.write(q["q"])

    user_answer = st.text_area("Your answer", key=f"answer_{i}")

    if st.button("Submit", key=f"submit_{i}"):

        # VALIDATION
        if not user_answer.strip():
            st.warning("Please enter an answer before submitting.")
            st.stop()

        dataset_info = str(df.head())

        result = grade_answer(
            question=q["q"],
            dataset_info=dataset_info,
            user_answer=user_answer
        )

        # SAFE SCORE
        try:
            score_line = result.split("\n")[0]
            score = int(score_line.replace("Score:", "").replace("%", "").strip())
        except:
            score = 70

        # XP
        xp = calculate_xp(score)

        # SAVE
        save_score(
            user_email=st.session_state.get("user", "guest"),
            score=score,
            challenge=q["q"],
            industry=st.session_state.get("industry"),
            xp=xp,
            challenge_type="practice"
        )

        st.info(f"You earned {xp} XP!")

        # STORE RESULT
        st.session_state[f"result_{i}"] = result

    # ---------------------------------
    # DISPLAY RESULT
    # ---------------------------------

    if f"result_{i}" in st.session_state:

        result = st.session_state[f"result_{i}"]
        score_line = result.split("\n")[0]

        st.write(f"### Result for Question {i+1}")

        if plan == "premium":

            st.success(result)

        else:

            st.write(score_line)

            from db import use_credit
            if st.session_state.get("answer_credits", 0) > 0:

                if st.button("🔓 Unlock Full Answer", key=f"unlock_{i}"):
                    success = use_credit(st.session_state["user_id"])

                    if success:
                        st.session_state.answer_credits -= 1
                        st.success(result)

                    else:

                        st.warning("⚠️ No credits left.")

                if st.button("🚀 Unlock Answer / Upgrade", key=f"upgrade_{i}"):
                    st.session_state.show_upgrade_popup = True


# ---------------------------------
# UPGRADE POPUP (GLOBAL)
# ---------------------------------

if st.session_state.get("show_upgrade_popup"):

    from payments import create_checkout_session

    st.markdown("---")
    st.subheader("🔓 Unlock Full Access")

    st.write("""
    You're close to becoming a top analyst.

    Upgrade to unlock full answers and advanced features.
    """)

    # 👇 get user email ONCE
    email = st.session_state.get("user")

    # 👇 create columns ONCE
    col1, col2 = st.columns(2)

    # -------------------------
    # ANSWER PACK
    # -------------------------
    with col1:
        st.subheader("💡 $5 — Answer Pack")

        if st.button("Buy 2 Answers", use_container_width=True):

            if not email:
                st.error("Please login first")
            else:
                url = create_checkout_session("answers", email)

                if url:
                    st.link_button("👉 Pay Now", url, use_container_width=True)
                else:
                    st.error("⚠️ Payment system not ready yet.")

    # -------------------------
    # PREMIUM
    # -------------------------
    with col2:
        st.subheader("🚀 $20/month — Premium")

        if st.button("Go Premium", use_container_width=True):

            if not email:
                st.error("Please login first")
            else:
                url = create_checkout_session("premium", email)

                if url:
                    st.link_button("👉 Upgrade Now", url, use_container_width=True)
                else:
                    st.error("⚠️ Payment system not ready yet.")
import streamlit as st
from data_loader import load_industry_data
from ai_engine.manager_agent import generate_manager_question
from ai_engine.grader import grade_answer
from ai_engine.scenario_generator import generate_business_scenario

st.title("AI Business Manager")

# ----------------------------
# Load Dataset
# ----------------------------

df = load_industry_data()

if df is None:
    st.warning("Please select an industry first")
    st.stop()

industry = st.session_state.get("industry", "business")

st.subheader("Dataset Preview")
st.dataframe(df.head())


# ----------------------------
# Generate Business Scenario
# ----------------------------

st.subheader("Business Scenario")

if st.button("Generate Business Scenario"):

    scenario = generate_business_scenario(
        industry=industry,
        dataset_preview=str(df.head())
    )

    st.session_state["scenario"] = scenario


if "scenario" in st.session_state:

    st.info(st.session_state["scenario"])


# ----------------------------
# Generate Manager Question
# ----------------------------

if st.button("Ask Manager Question"):

    question = generate_manager_question(
        dataset_preview=str(df.head()),
        industry=industry
    )

    st.session_state["manager_question"] = question


# ----------------------------
# Show Manager Question
# ----------------------------

if "manager_question" in st.session_state:

    st.subheader("Manager Request")

    st.write(st.session_state["manager_question"])

    user_answer = st.text_area("Your response to the manager")

    if st.button("Submit Report"):

        result = grade_answer(
            question=st.session_state["manager_question"],
            dataset_info=str(df.head()),
            user_answer=user_answer
        )

        plan = st.session_state.get("plan", "visitor")

        if plan == "premium":

            st.success(result)

        else:

            score_line = result.split("\n")[0]

            st.write(score_line)

            st.warning("Upgrade to premium to see full feedback.")

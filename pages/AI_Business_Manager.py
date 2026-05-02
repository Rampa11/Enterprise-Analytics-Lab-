import streamlit as st
from data_loader import load_industry_data
from ai_engine.consulting_projects import generate_consulting_project
from ai_engine.grader import grade_answer
from ai_engine.leaderboard import save_score

st.title("AI Business Manager")

# ---------------------------------
# Load dataset
# ---------------------------------

df = load_industry_data()

if df is None:
    st.warning("Please select an industry first")
    st.stop()

industry = st.session_state.get("industry", "business")

st.subheader("Dataset Preview")
st.dataframe(df.head())


# ---------------------------------
# Manager role selection
# ---------------------------------

manager_role = st.selectbox(
    "Choose Manager",
    [
        "operations_manager",
        "finance_manager",
        "product_manager",
        "hr_manager",
        "project_manager"
    ]
)


# ---------------------------------
# Generate consulting project
# ---------------------------------

if st.button("Generate Consulting Project"):

    project = generate_consulting_project(
        dataset_preview=str(df.head()),
        industry=industry,
        manager_role=manager_role
    )

    st.session_state["consulting_project"] = project


# ---------------------------------
# Display project
# ---------------------------------

if "consulting_project" in st.session_state:

    st.subheader("Consulting Project")

    st.info(st.session_state["consulting_project"])

    user_answer = st.text_area("Submit your analysis")

    if st.button("Submit Project"):

        result = grade_answer(
            question=st.session_state["consulting_project"],
            dataset_info=str(df.head()),
            user_answer=user_answer
        )

        score_line = result.split("\n")[0]
        score = int(score_line.replace("Score:", "").replace("%", "").strip())

        # Manager challenges give heavier XP
        xp = 100

        save_score(
            user_email=st.session_state.get("user"),
            score=score,
            challenge=st.session_state["consulting_project"],
            industry=industry,
            xp=xp,
            challenge_type=manager_role
        )

        st.success(result)
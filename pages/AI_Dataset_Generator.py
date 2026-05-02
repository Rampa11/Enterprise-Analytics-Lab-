import streamlit as st
from ai_engine.dataset_generator import generate_dataset_structure, create_dataset

st.title("AI Dataset Generator")

industry = st.selectbox(
    "Select Industry",
    [
        "Banking",
        "Retail",
        "Healthcare",
        "Logistics",
        "Manufacturing"
    ]
)

# ------------------------------
# Generate Dataset Structure
# ------------------------------

if st.button("Generate Dataset Structure"):

    structure = generate_dataset_structure(industry)

    st.session_state["dataset_structure"] = structure

    st.subheader("Generated Dataset Columns")

    st.text(structure)


# ------------------------------
# Create Dataset
# ------------------------------

if "dataset_structure" in st.session_state:

    columns = [
        line.strip()
        for line in st.session_state["dataset_structure"].split("\n")
        if line.strip()
    ]

    if st.button("Create Dataset"):

        df = create_dataset(columns)

        st.subheader("Dataset Preview")

        st.dataframe(df.head())

        csv = df.to_csv(index=False)

        st.download_button(
            "Download Dataset",
            csv,
            "generated_dataset.csv",
            "text/csv"
        )

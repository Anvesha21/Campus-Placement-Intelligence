"""Author: Anveshaa Kesharwaani

Streamlit app: enter a student profile and get an estimated placement
probability, a band, and advice on what to improve.

Run from the project root:
    streamlit run app.py
"""
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from src.advisor import advise, band
from src.features import BRANCHES, to_matrix
from src.whatif import plan, simulate

MODEL_PATH = Path("models/placement_model.joblib")
DATA_PATH = Path("data/students.csv")

st.set_page_config(page_title="Campus Placement Intelligence 2026", page_icon="🎓", layout="wide")
st.title("Campus Placement Intelligence 2026")
st.caption(
    "Demo on synthetic data. The estimate shows patterns in fictional data. "
    "It is not a prediction about any real student."
)


@st.cache_resource
def load_bundle():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_students():
    return pd.read_csv(DATA_PATH)


if not MODEL_PATH.exists() or not DATA_PATH.exists():
    st.error("Data or model not found. Run `python run_pipeline.py` from the project root first.")
    st.stop()

bundle = load_bundle()
students = load_students()

with st.form("profile"):
    col1, col2 = st.columns(2)
    with col1:
        branch = st.selectbox("Branch", BRANCHES)
        cgpa = st.slider("CGPA", 5.0, 10.0, 7.5, 0.1)
        backlogs = st.number_input("Active backlogs", 0, 4, 0)
        internships = st.number_input("Internships completed", 0, 4, 1)
        projects = st.number_input("Projects built", 0, 8, 2)
        certifications = st.number_input("Certifications", 0, 8, 1)
    with col2:
        coding = st.slider("Coding test score", 0.0, 100.0, 55.0, 0.5)
        aptitude = st.slider("Aptitude score", 0.0, 100.0, 60.0, 0.5)
        communication = st.slider("Communication score", 0.0, 100.0, 62.0, 0.5)
        mock = st.number_input("Mock interviews done", 0, 10, 2)
        data_tools = st.slider("Excel / SQL / Power BI score", 0.0, 100.0, 45.0, 0.5)
    submitted = st.form_submit_button("Check my chances")

if submitted:
    profile = pd.DataFrame([{
        "branch": branch,
        "cgpa": cgpa,
        "backlogs": backlogs,
        "internships": internships,
        "projects": projects,
        "certifications": certifications,
        "coding_score": coding,
        "aptitude_score": aptitude,
        "communication_score": communication,
        "mock_interviews": mock,
        "data_tools_score": data_tools,
    }])

    X = to_matrix(profile)[bundle["features"]]
    prob = float(bundle["model"].predict_proba(X)[0, 1])

    st.subheader("Result")
    st.metric("Estimated placement probability", f"{prob:.0%}")
    st.write(f"Band: **{band(prob)}**  |  Model: {bundle['model_name'].replace('_', ' ')}")

    student = profile.iloc[0].to_dict()

    tab_advice, tab_whatif, tab_plan = st.tabs(["What to work on first", "What-if simulator", "3-step plan"])

    with tab_advice:
        tips = advise(student, students)
        if tips:
            for tip in tips:
                st.write(f"- {tip}")
        else:
            st.write("No large gaps against the placed-student profile. Keep building on what you have.")

    with tab_whatif:
        st.write("Each row changes ONE thing and keeps everything else the same.")
        sim = simulate(student, bundle)
        if sim.empty:
            st.write("Every option is already at its limit.")
        else:
            st.bar_chart(sim.set_index("action")["uplift_points"])
            st.dataframe(sim, hide_index=True, use_container_width=True)

    with tab_plan:
        st.write("Best action first. Each step is measured after the steps before it.")
        steps = plan(student, bundle, steps=3)
        if steps.empty:
            st.write("No further step improves the estimate.")
        else:
            st.dataframe(steps, hide_index=True, use_container_width=True)

    st.caption(
        "The what-if numbers show how the MODEL reacts to a change. "
        "They are not a promise that the change causes an offer."
    )

st.divider()
st.caption("Built by Anveshaa Kesharwaani. Code licensed under MIT (see LICENSE).")

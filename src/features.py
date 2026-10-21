"""Author: Anveshaa Kesharwaani

Feature definitions shared by training, the advisor, and the Streamlit app.
Personal identifiers (name, gender, caste, religion, address) are never used.
"""
import pandas as pd

BRANCHES = ["CSE", "ECE", "IT", "EE", "ME"]

NUMERIC_FEATURES = [
    "cgpa",
    "backlogs",
    "internships",
    "projects",
    "certifications",
    "coding_score",
    "aptitude_score",
    "communication_score",
    "mock_interviews",
    "data_tools_score",
]

# CSE is the baseline branch, so it gets no dummy column.
BRANCH_FEATURES = [f"branch_{b}" for b in BRANCHES if b != "CSE"]

FEATURE_COLUMNS = NUMERIC_FEATURES + BRANCH_FEATURES
TARGET = "placed"


def to_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Turn a students DataFrame into the model's feature matrix."""
    X = df[NUMERIC_FEATURES].astype(float).copy()
    for branch in BRANCHES:
        if branch == "CSE":
            continue
        X[f"branch_{branch}"] = (df["branch"] == branch).astype(int).values
    return X[FEATURE_COLUMNS]

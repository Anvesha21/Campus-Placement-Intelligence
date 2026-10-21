"""Author: Anveshaa Kesharwaani

Export CSV files for Power BI and Tableau into bi_data/.

- One CSV per SQL view (the SQL layer is the source of truth).
- students_scored.csv: one row per student from vw_student_flat, plus an AI
  placement probability and band.

The AI probability is OUT-OF-FOLD: each student is scored by a model that did
not see that student during training (5-fold cross-validation). Scoring
students with a model trained on them would make the numbers look better
than they are.
"""
import sqlite3
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from src.advisor import advise, band
from src.features import TARGET, to_matrix
from src.train_model import candidate_models

DB_PATH = Path("data/placement.db")
MODEL_PATH = Path("models/placement_model.joblib")
BI_DIR = Path("bi_data")

VIEWS = [
    "vw_branch_summary",
    "vw_cgpa_band",
    "vw_backlog_impact",
    "vw_skill_gap",
    "vw_sector_offers",
    "vw_non_tech_share",
    # v2 views (window functions)
    "vw_branch_rank",
    "vw_readiness_segments",
    "vw_package_quartiles",
    "vw_funnel",
    "vw_package_bands",
]


def export(db_path=DB_PATH, model_path=MODEL_PATH, bi_dir=BI_DIR) -> dict:
    bi_dir = Path(bi_dir)
    bi_dir.mkdir(parents=True, exist_ok=True)
    model_name = joblib.load(model_path)["model_name"]

    written = {}
    conn = sqlite3.connect(db_path)
    try:
        for view in VIEWS:
            df = pd.read_sql(f"SELECT * FROM {view}", conn)
            df.to_csv(bi_dir / f"{view}.csv", index=False)
            written[f"{view}.csv"] = len(df)
        flat = pd.read_sql("SELECT * FROM vw_student_flat ORDER BY student_id", conn)
    finally:
        conn.close()

    X = to_matrix(flat)
    y = flat[TARGET]
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    prob = cross_val_predict(
        candidate_models()[model_name], X, y, cv=cv, method="predict_proba"
    )[:, 1]

    flat["ai_probability"] = prob.round(3)
    flat["ai_band"] = [band(p) for p in prob]
    # Lets Power BI / Tableau sort bands in a sensible order, not alphabetically.
    flat["ai_band_sort"] = flat["ai_band"].map({"Needs work": 1, "Moderate": 2, "Strong": 3})
    # Largest gap versus the median placed student (see src/advisor.py).
    no_gap = "No large gaps against the placed-student profile."
    flat["top_advice"] = [
        (advise(row, flat, top_n=1) or [no_gap])[0] for row in flat.to_dict("records")
    ]
    flat["is_tech"] = flat["is_tech"].astype("Int64")  # keeps 1/0, blank when not placed
    flat.to_csv(bi_dir / "students_scored.csv", index=False)
    written["students_scored.csv"] = len(flat)
    return written


if __name__ == "__main__":
    for name, rows in export().items():
        print(f"{name}: {rows} rows")

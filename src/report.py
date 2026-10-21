"""Author: Anveshaa Kesharwaani

Write reports/summary.md. Every number comes from the database views or the
saved model metrics, so the report updates whenever the pipeline runs.
"""
import json
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("data/placement.db")
REPORT_DIR = Path("reports")


def _query(db_path, sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    try:
        return pd.read_sql(sql, conn)
    finally:
        conn.close()


def write_summary(db_path=DB_PATH, report_dir=REPORT_DIR) -> Path:
    report_dir = Path(report_dir)
    metrics = json.loads((report_dir / "metrics.json").read_text())
    drivers = pd.read_csv(report_dir / "feature_drivers.csv")
    overall = _query(db_path, "SELECT COUNT(*) AS students FROM students").iloc[0]
    non_tech = _query(db_path, "SELECT * FROM vw_non_tech_share").iloc[0]
    branches = _query(db_path, "SELECT * FROM vw_branch_summary ORDER BY placement_rate_pct DESC")
    best = metrics["models"][metrics["best_model"]]

    lines = [
        "# Campus Placement Intelligence: Summary",
        "",
        "Author: Anveshaa Kesharwaani",
        "",
        "> All data is synthetic (fictional). These numbers show how the pipeline works.",
        "> They are not facts about any real college.",
        "",
        "## Headline numbers",
        "",
        f"- Students: {int(overall['students'])}",
        f"- Placement rate: {metrics['placement_rate_pct']}%",
        f"- Share of offers from non-tech companies: {non_tech['non_tech_offer_pct']}%",
        f"- Average package, non-tech vs tech: {non_tech['non_tech_avg_package_lpa']} vs "
        f"{non_tech['tech_avg_package_lpa']} LPA",
        "",
        "## Placement rate by branch",
        "",
        "| Branch | Students | Placed | Rate % | Avg package (LPA) |",
        "|---|---|---|---|---|",
    ]
    for _, r in branches.iterrows():
        lines.append(
            f"| {r['branch']} | {int(r['students'])} | {int(r['placed'])} | "
            f"{r['placement_rate_pct']} | {r['avg_package_lpa']} |"
        )

    lines += [
        "",
        "## Model",
        "",
        f"- Model used: **{metrics['best_model']}**",
        "- Rule: the explainable logistic regression is kept unless another model beats it "
        "by more than 0.01 cross-validated ROC-AUC.",
        f"- Test ROC-AUC: {best['test_roc_auc']}",
        f"- Test accuracy: {best['test_accuracy']}",
        f"- Test precision: {best['test_precision']}, recall: {best['test_recall']}",
        "",
        "## Top 5 factors (logistic regression coefficients)",
        "",
        "Positive means the factor raises placement odds. Negative means it lowers them.",
        "",
        "| Feature | Coefficient |",
        "|---|---|",
    ]
    for _, r in drivers.head(5).iterrows():
        lines.append(f"| {r['feature']} | {r['coefficient']} |")

    out = report_dir / "summary.md"
    out.write_text("\n".join(lines) + "\n")
    return out


if __name__ == "__main__":
    print("Summary written to", write_summary())

"""Author: Anveshaa Kesharwaani

Draw reports/insights_2026.png: a dark, four-panel picture of the v2 analysis.

1. Readiness segments (SQL: vw_readiness_segments)
2. Offers by package quartile (SQL: vw_package_quartiles)
3. Funnel from all students to placed (SQL: vw_funnel)
4. What-if uplift for a median-profile student (model: src/whatif.py)

Drawn with matplotlib. It is not a Power BI or Tableau screenshot.
"""
import sqlite3
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from src.whatif import median_student, simulate  # noqa: E402

DB_PATH = Path("data/placement.db")
MODEL_PATH = Path("models/placement_model.joblib")
REPORT_DIR = Path("reports")

BG, PANEL, INK, MUTED = "#0b1020", "#131a30", "#e6eaf5", "#93a0bd"
COLORS = ["#6366f1", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444"]


def _style(ax, title):
    ax.set_facecolor(PANEL)
    ax.set_title(title, color=INK, fontsize=12, loc="left", pad=10, fontweight="bold")
    ax.tick_params(colors=MUTED, labelsize=9)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#232c49")


def make_insights(db_path=DB_PATH, model_path=MODEL_PATH, report_dir=REPORT_DIR) -> Path:
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        seg = pd.read_sql("SELECT * FROM vw_readiness_segments ORDER BY segment", conn)
        quart = pd.read_sql("SELECT * FROM vw_package_quartiles ORDER BY quartile", conn)
        funnel = pd.read_sql("SELECT * FROM vw_funnel ORDER BY stage_no", conn)
        students = pd.read_sql("SELECT * FROM students", conn)
    finally:
        conn.close()

    bundle = joblib.load(model_path)
    sim = simulate(median_student(students), bundle).head(6).iloc[::-1]

    fig, axes = plt.subplots(2, 2, figsize=(14, 8.5), facecolor=BG)
    fig.suptitle("Campus Placement Intelligence 2026: deeper look", color=INK,
                 fontsize=16, fontweight="bold", x=0.06, ha="left")
    fig.text(0.06, 0.925, "Anveshaa Kesharwaani  |  synthetic data", color=MUTED, fontsize=10)

    ax = axes[0, 0]
    _style(ax, "Placement rate by readiness segment (%)")
    labels = [s.split(". ", 1)[1] for s in seg["segment"]]
    ax.bar(labels, seg["placement_rate_pct"], color=COLORS[:3])
    for i, v in enumerate(seg["placement_rate_pct"]):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center", color=INK, fontsize=10)
    ax.set_ylim(0, max(seg["placement_rate_pct"]) * 1.2)

    ax = axes[0, 1]
    _style(ax, "Average package by offer quartile (LPA)")
    ax.bar([f"Q{q}" for q in quart["quartile"]], quart["avg_lpa"], color=COLORS[1])
    for i, v in enumerate(quart["avg_lpa"]):
        ax.text(i, v + 0.3, f"{v:.1f}", ha="center", color=INK, fontsize=10)
    ax.set_ylim(0, max(quart["avg_lpa"]) * 1.2)

    ax = axes[1, 0]
    _style(ax, "Funnel: from all students to placed")
    ax.barh(funnel["stage"].iloc[::-1], funnel["students"].iloc[::-1], color=COLORS[0])
    for y, (n, p) in enumerate(zip(funnel["students"].iloc[::-1], funnel["pct_of_all"].iloc[::-1])):
        ax.text(n + 12, y, f"{n}  ({p:.0f}%)", va="center", color=INK, fontsize=10)
    ax.set_xlim(0, funnel["students"].max() * 1.25)

    ax = axes[1, 1]
    _style(ax, "What-if: chance of placement (+ points)")
    ax.barh(sim["action"], sim["uplift_points"], color=COLORS[2])
    for y, v in enumerate(sim["uplift_points"]):
        ax.text(v + 0.1, y, f"+{v:.1f}", va="center", color=INK, fontsize=10)
    ax.set_xlim(0, max(sim["uplift_points"].max() * 1.25, 1))

    fig.tight_layout(rect=(0.02, 0.02, 0.98, 0.9), w_pad=3)
    path = report_dir / "insights_2026.png"
    fig.savefig(path, dpi=130, facecolor=BG)
    plt.close(fig)
    return path


if __name__ == "__main__":
    print(make_insights())

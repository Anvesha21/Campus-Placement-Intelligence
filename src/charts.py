"""Author: Anveshaa Kesharwaani

Save the charts for the report as PNG files in reports/.
"""
import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no window needed; works on servers and in tests
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

DB_PATH = Path("data/placement.db")
REPORT_DIR = Path("reports")


def _query(db_path, sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    try:
        return pd.read_sql(sql, conn)
    finally:
        conn.close()


def _save_bar(labels, values, title, path):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels, values = list(labels), list(values)
    ax.bar([str(x) for x in labels], values, color="#2b6cb0")
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=30)
    for i, v in enumerate(values):
        ax.text(i, v, f"{v:g}", ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _save_barh(labels, values, title, path):
    fig, ax = plt.subplots(figsize=(8, 5))
    labels, values = list(labels), list(values)
    colors = ["#2f855a" if v >= 0 else "#c53030" for v in values]
    ax.barh(labels, values, color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.invert_yaxis()
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def make_charts(db_path=DB_PATH, report_dir=REPORT_DIR):
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    branch = _query(
        db_path,
        "SELECT branch, placement_rate_pct FROM vw_branch_summary ORDER BY placement_rate_pct DESC",
    )
    _save_bar(branch["branch"], branch["placement_rate_pct"],
              "Placement rate by branch (%)", report_dir / "branch_placement_rate.png")

    band = _query(db_path, "SELECT cgpa_band, placement_rate_pct FROM vw_cgpa_band")
    _save_bar(band["cgpa_band"], band["placement_rate_pct"],
              "Placement rate by CGPA band (%)", report_dir / "cgpa_vs_placement.png")

    sector = _query(
        db_path,
        "SELECT sector, offers FROM vw_sector_offers ORDER BY offers DESC",
    )
    _save_bar(sector["sector"], sector["offers"],
              "Offers by sector", report_dir / "offers_by_sector.png")

    drivers = pd.read_csv(report_dir / "feature_drivers.csv")
    _save_barh(drivers["feature"], drivers["coefficient"],
               "What pushes placement up or down (logistic regression)",
               report_dir / "model_drivers.png")

    return sorted(p.name for p in report_dir.glob("*.png"))


if __name__ == "__main__":
    print("Charts saved:", make_charts())

"""Author: Anveshaa Kesharwaani

Create two pictures for the README:
- architecture.png: how data flows through the project
- dashboard_preview.png: a LAYOUT PREVIEW of the dashboard, drawn with
  matplotlib from students_scored.csv. It is not a Power BI or Tableau
  screenshot. Build the real dashboard with docs/powerbi_guide.md.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

BI_DIR = Path("bi_data")
REPORT_DIR = Path("reports")
BLUE, GREEN, GREY = "#2b6cb0", "#2f855a", "#4a5568"


def make_architecture(report_dir=REPORT_DIR) -> Path:
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")

    def box(x, y, title, sub):
        ax.add_patch(FancyBboxPatch((x, y), 2.6, 1.4, boxstyle="round,pad=0.05",
                                    fc="#ebf4ff", ec=BLUE, lw=1.5))
        ax.text(x + 1.3, y + 0.95, title, ha="center", va="center", fontsize=10, weight="bold")
        ax.text(x + 1.3, y + 0.3, sub, ha="center", va="center", fontsize=8, color=GREY)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=15, color=GREY, lw=1.3))

    # Row A: build the data and the model
    box(0.2, 5.2, "generate_data.py", "Synthetic students,\ncompanies, offers (CSV)")
    box(3.2, 5.2, "SQLite database", "schema.sql + views.sql\n3 tables, 7 views")
    box(6.2, 5.2, "train_model.py", "Logistic regression vs\nrandom forest (CV)")
    box(9.2, 5.2, "Saved model", "models/placement_model\n.joblib")
    arrow(2.85, 5.9, 3.15, 5.9)
    arrow(5.85, 5.9, 6.15, 5.9)
    arrow(8.85, 5.9, 9.15, 5.9)

    # Row B: export for BI tools, and the Streamlit app
    box(3.2, 2.9, "export_bi.py", "Reads the database views\nand scores every student")
    box(9.2, 2.9, "Streamlit app", "app.py: chances and advice\nfor one student")
    arrow(4.5, 5.2, 4.5, 4.35)        # database -> export
    arrow(9.5, 5.2, 5.85, 4.1)        # saved model -> export (AI score)
    arrow(10.5, 5.2, 10.5, 4.35)      # saved model -> Streamlit

    # Row C: dashboards
    box(1.7, 0.5, "Power BI", "docs/powerbi_guide.md\n3-page dashboard")
    box(4.7, 0.5, "Tableau Public", "docs/tableau_guide.md\nsame data, same questions")
    ax.text(7.6, 1.2, "bi_data/students_scored.csv\nand one CSV per SQL view",
            ha="left", va="center", fontsize=9, color=GREY, style="italic")
    arrow(4.5, 2.9, 3.0, 1.95)
    arrow(4.5, 2.9, 6.0, 1.95)

    ax.set_title("Campus Placement Intelligence: data flow", fontsize=13, weight="bold")
    out = report_dir / "architecture.png"
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def make_dashboard_preview(bi_dir=BI_DIR, report_dir=REPORT_DIR) -> Path:
    bi_dir, report_dir = Path(bi_dir), Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(bi_dir / "students_scored.csv")

    placed = df[df["placed"] == 1]
    kpis = [
        ("Students", f"{len(df):,}"),
        ("Placement rate", f"{df['placed'].mean():.1%}"),
        ("Avg package (LPA)", f"{placed['package_lpa'].mean():.2f}"),
        ("Non-tech share of offers", f"{(placed['is_tech'] == 0).mean():.1%}"),
    ]

    fig = plt.figure(figsize=(14, 8.5))
    fig.suptitle("Placement dashboard: layout preview (matplotlib, not a Power BI screenshot)",
                 fontsize=13, weight="bold")
    for i, (label, value) in enumerate(kpis):
        ax = fig.add_axes([0.04 + i * 0.24, 0.80, 0.22, 0.10])
        ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02",
                                    fc="#ebf4ff", ec=BLUE, transform=ax.transAxes))
        ax.text(0.5, 0.62, value, ha="center", va="center", fontsize=20,
                weight="bold", color=BLUE, transform=ax.transAxes)
        ax.text(0.5, 0.2, label, ha="center", va="center", fontsize=10,
                color=GREY, transform=ax.transAxes)

    def bar(ax, series, title, color=BLUE, horizontal=False, fmt="{:.0f}"):
        if horizontal:
            ax.barh([str(i) for i in series.index], series.values, color=color)
            ax.invert_yaxis()
            for y, v in enumerate(series.values):
                ax.text(v, y, " " + fmt.format(v), va="center", fontsize=8)
        else:
            ax.bar([str(i) for i in series.index], series.values, color=color)
            for x, v in enumerate(series.values):
                ax.text(x, v, fmt.format(v), ha="center", va="bottom", fontsize=8)
            ax.tick_params(axis="x", rotation=20)
        ax.set_title(title, fontsize=10, weight="bold")

    by_branch = (df.groupby("branch")["placed"].mean() * 100).sort_values(ascending=False)
    by_band = df.groupby("cgpa_band")["placed"].mean() * 100
    by_sector = placed.groupby("sector")["package_lpa"].mean().sort_values(ascending=False)
    needs_help = df[(df["placed"] == 0) & (df["ai_band"] == "Needs work")]
    help_by_branch = needs_help.groupby("branch").size().sort_values(ascending=False)

    bar(fig.add_axes([0.06, 0.45, 0.40, 0.28]), by_branch, "Placement rate by branch (%)", fmt="{:.1f}")
    bar(fig.add_axes([0.56, 0.45, 0.40, 0.28]), by_band, "Placement rate by CGPA band (%)", fmt="{:.1f}")
    bar(fig.add_axes([0.14, 0.07, 0.32, 0.28]), by_sector, "Average package by sector (LPA)",
        color=GREEN, horizontal=True, fmt="{:.1f}")
    bar(fig.add_axes([0.56, 0.07, 0.40, 0.28]), help_by_branch,
        "Unplaced students scored 'Needs work', by branch", color="#c53030")

    out = report_dir / "dashboard_preview.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


if __name__ == "__main__":
    print(make_architecture())
    print(make_dashboard_preview())

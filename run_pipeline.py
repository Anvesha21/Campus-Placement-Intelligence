"""Author: Anveshaa Kesharwaani

Run the whole project in order:
data -> database -> model -> charts -> summary -> BI files -> pictures
-> v2 insights picture -> interactive HTML dashboard.

Usage (from the project root folder):
    python run_pipeline.py                      # creates synthetic data first
    python run_pipeline.py --use-existing-data  # keeps the CSV files already in data/
"""
import sys

from src.build_database import build
from src.charts import make_charts
from src.export_bi import export
from src.generate_data import main as generate
from src.html_dashboard import build_dashboard
from src.images import make_architecture, make_dashboard_preview
from src.insights_image import make_insights
from src.report import write_summary
from src.train_model import train


def main():
    if "--use-existing-data" in sys.argv:
        print("1/9 Using the existing CSV files in data/")
    else:
        print("1/9 Generating synthetic data")
        generate()

    print("2/9 Building SQLite database")
    print("    rows:", build())

    print("3/9 Training models")
    metrics = train()
    print("    model used:", metrics["best_model"])

    print("4/9 Saving charts")
    print("    files:", make_charts())

    print("5/9 Writing summary")
    print("    ", write_summary())

    print("6/9 Exporting CSV files for Power BI and Tableau")
    for name, rows in export().items():
        print(f"    {name}: {rows} rows")

    print("7/9 Creating architecture diagram and dashboard preview")
    print("    ", make_architecture())
    print("    ", make_dashboard_preview())

    print("8/9 Drawing v2 insights picture (segments, quartiles, funnel, what-if)")
    print("    ", make_insights())

    print("9/9 Building the interactive HTML dashboard")
    print("    ", build_dashboard())

    print("\nDone. Open dashboard/index.html in your browser, then")
    print("build the Power BI dashboard with docs/powerbi_guide.md,")
    print("or run: streamlit run app.py")


if __name__ == "__main__":
    main()

# Build the Power BI dashboard

Author: Anveshaa Kesharwaani

This guide builds a 3-page dashboard from the CSV files in `bi_data/`. No coding is needed once the files exist. Allow 2 to 3 hours the first time.

**You need:** Power BI Desktop (free from Microsoft, Windows only). On a Mac, use the Tableau guide instead, or a Windows PC.

> The data is synthetic (fictional). Do not publish a dashboard built on real student records to the public web.

## Step 1: Load the data

1. Open Power BI Desktop. Click **Get data**, then **Text/CSV**.
2. Select `bi_data/students_scored.csv`. Click **Transform Data**.
3. In Power Query, check these types (the column header icon shows the type):
   - Whole number: `student_id`, `backlogs`, `internships`, `projects`, `certifications`, `mock_interviews`, `placed`, `is_tech`, `ai_band_sort`
   - Decimal number: `cgpa`, `coding_score`, `aptitude_score`, `communication_score`, `data_tools_score`, `package_lpa`, `ai_probability`
   - Text: `branch`, `cgpa_band`, `placement_status`, `company_name`, `sector`, `company_type`, `ai_band`, `top_advice`
4. Click **Close & Apply**.
5. Repeat **Get data, Text/CSV** for `bi_data/vw_skill_gap.csv`. You will use it on page 2.

Blank cells in `package_lpa`, `sector`, and `company_type` are correct. They belong to students who were not placed.

## Step 2: Sort the AI band properly

1. In the **Data** pane, click the `ai_band` column.
2. On the top menu choose **Column tools**, then **Sort by column**, then `ai_band_sort`.

Without this, the bands sort alphabetically (Moderate, Needs work, Strong).

## Step 3: Create the measures

Click the `students_scored` table, then **Table tools**, then **New measure**. Paste one measure at a time.

```dax
Students = COUNTROWS ( students_scored )

Placed Students =
CALCULATE ( COUNTROWS ( students_scored ), students_scored[placed] = 1 )

Placement Rate = DIVIDE ( [Placed Students], [Students] )

Avg Package LPA = AVERAGE ( students_scored[package_lpa] )

Non Tech Offer Share =
DIVIDE (
    CALCULATE ( COUNTROWS ( students_scored ), students_scored[company_type] = "Non-tech" ),
    [Placed Students]
)

Avg AI Probability = AVERAGE ( students_scored[ai_probability] )
```

Select `Placement Rate` and `Non Tech Offer Share`, then in **Measure tools** set the format to **Percentage** with 1 decimal place. Set `Avg Package LPA` to 2 decimal places.

**Check your work.** With no filters applied, the cards should show:

| Measure | Expected |
|---|---|
| Students | 1,200 |
| Placement Rate | 57.7% |
| Avg Package LPA | 9.39 |
| Non Tech Offer Share | 38.7% |

If a number differs, a data type from Step 1 is probably wrong.

## Step 4: Page 1, Overview

Rename the page to **Overview**.

1. Four **Card** visuals: `Students`, `Placement Rate`, `Avg Package LPA`, `Non Tech Offer Share`.
2. **Clustered column chart.** X-axis: `branch`. Y-axis: `Placement Rate`. Title: "Placement rate by branch".
3. **Clustered column chart.** X-axis: `cgpa_band`. Y-axis: `Placement Rate`. Title: "Placement rate by CGPA band".
4. **Clustered bar chart.** Y-axis: `sector`. X-axis: `Avg Package LPA`. In the **Filters** pane, set the visual filter on `sector` to **is not blank**. Sort by `Avg Package LPA` descending.
5. **Slicer** on `branch`.

## Step 5: Page 2, Skills and AI

Add a new page named **Skills and AI**.

1. **Clustered bar chart** from the `vw_skill_gap` table. Y-axis: `skill`. X-axis: `placed_avg` and `not_placed_avg`. Visual filter on `skill`: tick only `coding_score`, `aptitude_score`, `communication_score`, `data_tools_score` (they share a 0 to 100 scale). Title: "Average score: placed vs not placed".
2. **Clustered column chart.** X-axis: `ai_band`. Y-axis: `Placement Rate`. Title: "Does the AI score separate students?" Bars should rise from Needs work to Strong. This is the check that the model works.
3. **Table** with columns `student_id`, `branch`, `cgpa`, `ai_probability`, `top_advice`. Visual filters: `placement_status` is `Not placed`, and `ai_band` is `Needs work`. Sort by `ai_probability` ascending. Title: "Unplaced students to support first".
4. **Slicer** on `branch`.

## Step 6: Page 3, Companies

Add a page named **Companies**.

1. **Clustered column chart.** X-axis: `company_type`. Y-axis: `Avg Package LPA`. Filter `company_type` to **is not blank**.
2. **Clustered bar chart.** Y-axis: `sector`. X-axis: `Placed Students`. Filter `sector` to **is not blank**.
3. **Donut chart.** Legend: `company_type`. Values: `Placed Students`. Filter `company_type` to **is not blank**.
4. **Slicer** on `branch`.

## Step 7: Finish and save

1. Add a text box on every page: "Synthetic data. Author: Anveshaa Kesharwaani".
2. Save as `placement_dashboard.pbix` in a `powerbi/` folder in the project.
3. Take a screenshot of each page. Save them in `docs/screenshots/` as `powerbi_overview.png`, `powerbi_skills_ai.png`, `powerbi_companies.png`.
4. Add them to the main `README.md`:

```markdown
![Overview](docs/screenshots/powerbi_overview.png)
![Skills and AI](docs/screenshots/powerbi_skills_ai.png)
![Companies](docs/screenshots/powerbi_companies.png)
```

## What the dashboard should tell you

- Placement rate rises with CGPA band. Compare your chart with `reports/cgpa_vs_placement.png`.
- Tech offers pay more than non-tech offers, but non-tech companies still give a large share of offers.
- Unplaced students scored "Needs work" are a practical list for a placement cell to prioritise.

## Troubleshooting

- **A card shows a wrong number.** Check the column types from Step 1. A number imported as text breaks the measures.
- **A bar labelled "(Blank)" appears.** Unplaced students have no sector or company type. Add the "is not blank" visual filter.
- **AI bands sort alphabetically.** Repeat Step 2 (Sort by column).
- **A measure gives a name error.** A measure cannot share its name with a column in the same table. None of the measures above do.

> These steps come from the standard Power BI Desktop workflow. Menu names can change slightly between versions. If a menu is missing, search for its name in the help box at the top of the window.

## Optional page 4: v2 insights

Load these extra CSV files from `bi_data/` the same way as in Step 1:
`vw_funnel.csv`, `vw_readiness_segments.csv`, `vw_package_quartiles.csv`, `vw_package_bands.csv`, `vw_branch_rank.csv`.

1. **Funnel chart.** Category: `stage`. Values: `students`. Sort by `stage_no` (Step 2 method).
2. **Clustered column.** Axis: `segment`. Values: `placement_rate_pct`. Expect about 44.6% for "Foundation needed" and 64.5% for "Interview-ready".
3. **Column chart.** Axis: `quartile`. Values: `avg_lpa`. Expect about 5.1 for Q1 and 15.9 for Q4.
4. **Line and column.** Axis: `package_band`. Columns: `share_pct`. Line: `cumulative_pct`. The line must end at 100.
5. Save a screenshot as `docs/screenshots/powerbi_insights.png`.

Tableau: the same five files load as separate data sources. Build each chart on its own sheet, then combine them on one dashboard.

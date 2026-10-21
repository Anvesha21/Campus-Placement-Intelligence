# Build the Tableau dashboard

Author: Anveshaa Kesharwaani

This guide builds the same dashboard as the Power BI guide, using the same CSV files. Tableau Public is free and runs on Windows and Mac.

> Tableau Public saves workbooks to a public profile. That is fine for this synthetic data. Never publish real student records this way.

## Step 1: Connect to the data

1. Open Tableau Public. Under **Connect**, choose **Text file**.
2. Select `bi_data/students_scored.csv`.
3. On the Data Source tab, check that `placed`, `is_tech`, and `ai_band_sort` are numbers (whole). Click **Sheet 1**.

## Step 2: Create calculated fields

Go to **Analysis, Create Calculated Field**. Create each one, then set number formats by right-clicking the field, then **Default Properties, Number Format**.

| Name | Formula | Format |
|---|---|---|
| Placement Rate | `SUM([placed]) / COUNTD([student_id])` | Percentage, 1 decimal |
| Non-tech Offer Share | `SUM(IF [company_type] = "Non-tech" THEN 1 ELSE 0 END) / SUM([placed])` | Percentage, 1 decimal |
| Students | `COUNTD([student_id])` | Number, 0 decimals |

For average package, drag `package_lpa` to a view and change it to **Average** (right-click, **Measure, Average**). Tableau ignores blanks, so unplaced students do not affect it.

## Step 3: Build the sheets

Create one sheet per chart. Name each sheet clearly.

1. **KPI sheets.** One sheet each for `Students`, `Placement Rate`, `AVG(package_lpa)`, `Non-tech Offer Share`. Drag the measure onto **Text** in the Marks card.
2. **By branch.** Columns: `branch`. Rows: `Placement Rate`.
3. **By CGPA band.** Columns: `cgpa_band`. Rows: `Placement Rate`.
4. **Package by sector.** Rows: `sector`. Columns: `AVG(package_lpa)`. Right-click `sector` on the Filters shelf and exclude **Null**. Sort descending.
5. **AI score check.** Columns: `ai_band`. Rows: `Placement Rate`. To sort: right-click `ai_band`, **Sort**, **Sort by: Field**, choose `ai_band_sort`, aggregation **Minimum**, ascending. Bars should rise from Needs work to Strong.
6. **Students to support.** Drag `student_id`, `branch`, `cgpa`, `ai_probability`, `top_advice` to **Rows** as discrete fields. Filters: `placement_status` = Not placed, `ai_band` = Needs work.

## Step 4: Assemble the dashboard

1. Click **New Dashboard**. Set size to **Automatic** or **Range**.
2. Drag the four KPI sheets across the top, then the chart sheets below.
3. On the `By branch` sheet, click the filter icon on its dashboard frame and choose **Use as Filter**, so clicking a branch filters every other chart.
4. Add a text box: "Synthetic data. Author: Anveshaa Kesharwaani".

## Step 5: Check your numbers

With no filter, your KPIs should read:

| Measure | Expected |
|---|---|
| Students | 1,200 |
| Placement Rate | 57.7% |
| Average package | 9.39 LPA |
| Non-tech Offer Share | 38.7% |

## Step 6: Publish and screenshot

1. **File, Save to Tableau Public** and sign in. Copy the public link.
2. Save a screenshot of the dashboard to `docs/screenshots/tableau_dashboard.png`.
3. Add both to the main `README.md`:

```markdown
![Tableau dashboard](docs/screenshots/tableau_dashboard.png)
[Live Tableau dashboard](PASTE-YOUR-LINK-HERE)
```

> These steps follow the standard Tableau Public workflow. Menu names can change between versions.

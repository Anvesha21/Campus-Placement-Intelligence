# SQL views explained

Author: Anveshaa Kesharwaani

All SQL is in `sql/schema.sql` and `sql/views.sql`. You can open `data/placement.db` in the free tool DB Browser for SQLite and run any query below.

## Tables

| Table | One row is | Notes |
|---|---|---|
| `students` | one student | `placed` is 0 or 1. CHECK constraints keep scores in range. |
| `companies` | one company | `is_tech` is 1 for tech, 0 for non-tech. |
| `offers` | one job offer | At most one offer per student in this dataset. |

SQLite does not enforce foreign keys unless you switch them on. This project checks that offers match placed students in `tests/test_pipeline.py` instead.

## Views

A view is a saved query. It stores no data of its own and always shows the current table contents.

| View | Question it answers | How it works |
|---|---|---|
| `vw_branch_summary` | Which branch places best, and what does it pay? | Groups students by branch. Placement rate is placed students divided by all students. Average package comes from a subquery that joins `offers` to `students`. |
| `vw_cgpa_band` | Does a higher CGPA help? | A `CASE` expression sorts each student into one of four bands, then groups by band. The number prefix (1., 2., ...) makes bands sort correctly. |
| `vw_backlog_impact` | How much do backlogs hurt? | Groups by number of backlogs and computes the placement rate for each. |
| `vw_skill_gap` | Where do placed and unplaced students differ? | `AVG(CASE WHEN placed = 1 THEN score END)` averages only placed students, because `AVG` skips NULL. `UNION ALL` stacks one such row per skill. |
| `vw_sector_offers` | Which sectors give offers, and at what pay? | `LEFT JOIN` from companies to offers keeps sectors with zero offers. Share of offers divides by a subquery that counts all offers. |
| `vw_non_tech_share` | How big is the non-tech opportunity? | Joins offers to companies and uses `CASE` inside `SUM` and `AVG` to split tech and non-tech. |
| `vw_student_flat` | Everything about one student in one row | Two `LEFT JOIN`s attach offer and company details. Unplaced students keep a row with blank offer columns. This is the table Power BI and Tableau load. |

## More queries

`sql/analysis_queries.sql` has 8 more queries: `RANK`, a CTE, `NTILE`, a running total with a window frame, a cross-tab by CGPA, a support list, a top-10, and a data check. Some results (for example, ME having a high non-tech share) come from the weights in `src/generate_data.py`, so they show the query working, not a real-world fact.

## Practice queries

Run these in DB Browser for SQLite.

```sql
-- 1. High-CGPA students who are still unplaced
SELECT student_id, branch, cgpa
FROM students
WHERE cgpa >= 8 AND placed = 0
ORDER BY cgpa DESC
LIMIT 10;

-- 2. Average package by branch and company type
SELECT branch, company_type, ROUND(AVG(package_lpa), 2) AS avg_package, COUNT(*) AS offers
FROM vw_student_flat
WHERE placed = 1
GROUP BY branch, company_type
ORDER BY branch, company_type;

-- 3. Top 3 packages in each sector (window function)
SELECT * FROM (
    SELECT sector, student_id, package_lpa,
           ROW_NUMBER() OVER (PARTITION BY sector ORDER BY package_lpa DESC) AS rn
    FROM vw_student_flat
    WHERE placed = 1
)
WHERE rn <= 3;

-- 4. Share of students with at least one internship, by placement status
SELECT placement_status,
       ROUND(100.0 * SUM(CASE WHEN internships >= 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_with_internship
FROM vw_student_flat
GROUP BY placement_status;
```

## v2 views (sql/advanced_views.sql)

These five views use window functions. They need SQLite 3.25 or newer.

| View | Technique | Question it answers |
|---|---|---|
| `vw_branch_rank` | `RANK() OVER (ORDER BY ...)` | Which branch ranks first on placement rate, and which on pay? The two ranks can differ. |
| `vw_readiness_segments` | CTE + `CASE` | Do students with higher average skill scores place more often? (Foundation needed / Almost there / Interview-ready) |
| `vw_package_quartiles` | `NTILE(4)` | What do the lowest and highest quarter of offers pay? |
| `vw_funnel` | `FIRST_VALUE`, `LAG` | How many students remain after each filter: internship, CGPA 7+, no backlogs, placed? |
| `vw_package_bands` | `SUM() OVER` | What share of offers falls below 5, 8 and 12 LPA (running total)? |

**Interview tip.** Be ready to explain why `vw_funnel` uses `FIRST_VALUE` for "% of all" but `LAG` for "% of previous stage". The first compares every stage with the start. The second compares each stage with the stage just before it.

**Limit.** The segment cut-offs (48 and 58) are chosen by hand for this synthetic data. Real data needs its own cut-offs.

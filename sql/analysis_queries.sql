-- Author: Anveshaa Kesharwaani
-- Analysis queries for the placement database. Each block answers one question.
-- Run in any SQLite client, or from Python: sqlite3 data/placement.db < sql/analysis_queries.sql

-- 1. Rank branches by placement rate (window function)
SELECT
    branch,
    placement_rate_pct,
    RANK() OVER (ORDER BY placement_rate_pct DESC) AS rate_rank
FROM vw_branch_summary;

-- 2. Which branches get the most non-tech offers? (CTE + conditional aggregation)
WITH branch_offers AS (
    SELECT s.branch, c.is_tech, COUNT(*) AS offers
    FROM offers o
    JOIN students s  ON s.student_id  = o.student_id
    JOIN companies c ON c.company_id  = o.company_id
    GROUP BY s.branch, c.is_tech
)
SELECT
    branch,
    SUM(CASE WHEN is_tech = 0 THEN offers ELSE 0 END)                  AS non_tech_offers,
    SUM(offers)                                                        AS total_offers,
    ROUND(100.0 * SUM(CASE WHEN is_tech = 0 THEN offers ELSE 0 END)
          / SUM(offers), 1)                                            AS non_tech_share_pct
FROM branch_offers
GROUP BY branch
ORDER BY non_tech_share_pct DESC;

-- 3. Package quartile within each sector (NTILE window function)
SELECT
    c.sector,
    o.package_lpa,
    NTILE(4) OVER (PARTITION BY c.sector ORDER BY o.package_lpa) AS package_quartile
FROM offers o
JOIN companies c ON c.company_id = o.company_id
ORDER BY c.sector, o.package_lpa DESC;

-- 4. Running total of offers by sector, biggest sector first
SELECT
    sector,
    offers,
    SUM(offers) OVER (
        ORDER BY offers DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_offers
FROM vw_sector_offers
ORDER BY offers DESC;

-- 5. Cross-tab: placement rate by internships, split by CGPA (8 and above vs below 8)
SELECT
    CASE WHEN internships >= 3 THEN '3+' ELSE CAST(internships AS TEXT) END AS internships_group,
    ROUND(100.0 * SUM(CASE WHEN cgpa >= 8 THEN placed END)
          / SUM(CASE WHEN cgpa >= 8 THEN 1 END), 1)                        AS rate_cgpa_8_plus,
    ROUND(100.0 * SUM(CASE WHEN cgpa < 8 THEN placed END)
          / SUM(CASE WHEN cgpa < 8 THEN 1 END), 1)                         AS rate_cgpa_below_8
FROM students
GROUP BY internships_group
ORDER BY internships_group;

-- 6. Students who are not placed and have no internship and a low coding score.
--    A support list for the placement cell.
SELECT
    student_id,
    branch,
    cgpa,
    backlogs,
    coding_score
FROM students
WHERE placed = 0
  AND internships = 0
  AND coding_score < 50
ORDER BY coding_score ASC, cgpa ASC;

-- 7. Top 10 packages with the student's branch and company
SELECT
    s.student_id,
    s.branch,
    c.company_name,
    c.sector,
    o.package_lpa
FROM offers o
JOIN students s  ON s.student_id = o.student_id
JOIN companies c ON c.company_id = o.company_id
ORDER BY o.package_lpa DESC
LIMIT 10;

-- 8. Data check: placed students with no offer row (expected: 0)
SELECT COUNT(*) AS placed_without_offer
FROM students s
LEFT JOIN offers o ON o.student_id = s.student_id
WHERE s.placed = 1
  AND o.offer_id IS NULL;

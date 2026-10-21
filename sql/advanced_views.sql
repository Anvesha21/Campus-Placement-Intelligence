-- Author: Anveshaa Kesharwaani
-- Advanced analysis views (v2): window functions, CTEs, NTILE, cumulative share.
-- Needs SQLite 3.25 or newer for window functions. Loaded after views.sql.

-- 1. Branch ranking: RANK() over placement rate and over average package.
DROP VIEW IF EXISTS vw_branch_rank;
CREATE VIEW vw_branch_rank AS
SELECT
    branch,
    students,
    placement_rate_pct,
    avg_package_lpa,
    RANK() OVER (ORDER BY placement_rate_pct DESC) AS rate_rank,
    RANK() OVER (ORDER BY avg_package_lpa DESC)    AS package_rank
FROM vw_branch_summary;

-- 2. Readiness segments: average of the four skill scores, then a CASE bucket.
DROP VIEW IF EXISTS vw_readiness_segments;
CREATE VIEW vw_readiness_segments AS
WITH scored AS (
    SELECT
        student_id,
        placed,
        (coding_score + aptitude_score + communication_score + data_tools_score) / 4.0 AS readiness
    FROM students
),
seg AS (
    SELECT
        placed,
        readiness,
        CASE
            WHEN readiness >= 58 THEN '3. Interview-ready'
            WHEN readiness >= 48 THEN '2. Almost there'
            ELSE '1. Foundation needed'
        END AS segment
    FROM scored
)
SELECT
    segment,
    COUNT(*)                                   AS students,
    ROUND(100.0 * SUM(placed) / COUNT(*), 1)   AS placement_rate_pct,
    ROUND(AVG(readiness), 1)                   AS avg_readiness
FROM seg
GROUP BY segment;

-- 3. Package quartiles: NTILE(4) splits offers into four equal-sized groups.
DROP VIEW IF EXISTS vw_package_quartiles;
CREATE VIEW vw_package_quartiles AS
WITH ranked AS (
    SELECT package_lpa, NTILE(4) OVER (ORDER BY package_lpa) AS quartile
    FROM offers
)
SELECT
    quartile,
    COUNT(*)                     AS offers,
    ROUND(MIN(package_lpa), 2)   AS min_lpa,
    ROUND(AVG(package_lpa), 2)   AS avg_lpa,
    ROUND(MAX(package_lpa), 2)   AS max_lpa
FROM ranked
GROUP BY quartile;

-- 4. Funnel: how many students survive each filter. LAG() gives the step conversion.
DROP VIEW IF EXISTS vw_funnel;
CREATE VIEW vw_funnel AS
WITH stages AS (
    SELECT 1 AS stage_no, 'All students' AS stage, COUNT(*) AS students FROM students
    UNION ALL
    SELECT 2, 'Has 1+ internship', COUNT(*) FROM students WHERE internships >= 1
    UNION ALL
    SELECT 3, 'and CGPA 7+', COUNT(*) FROM students WHERE internships >= 1 AND cgpa >= 7
    UNION ALL
    SELECT 4, 'and no backlogs', COUNT(*) FROM students
        WHERE internships >= 1 AND cgpa >= 7 AND backlogs = 0
    UNION ALL
    SELECT 5, 'and placed', COUNT(*) FROM students
        WHERE internships >= 1 AND cgpa >= 7 AND backlogs = 0 AND placed = 1
)
SELECT
    stage_no,
    stage,
    students,
    ROUND(100.0 * students / FIRST_VALUE(students) OVER (ORDER BY stage_no), 1) AS pct_of_all,
    ROUND(100.0 * students / LAG(students) OVER (ORDER BY stage_no), 1)         AS pct_of_previous
FROM stages
ORDER BY stage_no;

-- 5. Cumulative package share: SUM() OVER builds a running total.
DROP VIEW IF EXISTS vw_package_bands;
CREATE VIEW vw_package_bands AS
WITH banded AS (
    SELECT
        CASE
            WHEN package_lpa < 5  THEN '1. Under 5 LPA'
            WHEN package_lpa < 8  THEN '2. 5 to under 8 LPA'
            WHEN package_lpa < 12 THEN '3. 8 to under 12 LPA'
            ELSE '4. 12 LPA and above'
        END AS package_band,
        COUNT(*) AS offers
    FROM offers
    GROUP BY package_band
)
SELECT
    package_band,
    offers,
    ROUND(100.0 * offers / SUM(offers) OVER (), 1)                              AS share_pct,
    ROUND(100.0 * SUM(offers) OVER (ORDER BY package_band) / SUM(offers) OVER (), 1) AS cumulative_pct
FROM banded;

-- Author: Anveshaa Kesharwaani
-- Analysis views. Each view answers one placement question.
-- The offers table has at most one row per student, so the joins below do not double count.

DROP VIEW IF EXISTS vw_branch_summary;
CREATE VIEW vw_branch_summary AS
SELECT
    s.branch,
    COUNT(*)                                  AS students,
    SUM(s.placed)                             AS placed,
    ROUND(100.0 * SUM(s.placed) / COUNT(*), 1) AS placement_rate_pct,
    ROUND((
        SELECT AVG(o.package_lpa)
        FROM offers o
        JOIN students x ON x.student_id = o.student_id
        WHERE x.branch = s.branch
    ), 2)                                     AS avg_package_lpa
FROM students s
GROUP BY s.branch;

DROP VIEW IF EXISTS vw_cgpa_band;
CREATE VIEW vw_cgpa_band AS
SELECT
    CASE
        WHEN cgpa < 7 THEN '1. Below 7'
        WHEN cgpa < 8 THEN '2. 7 to under 8'
        WHEN cgpa < 9 THEN '3. 8 to under 9'
        ELSE '4. 9 and above'
    END AS cgpa_band,
    COUNT(*) AS students,
    ROUND(100.0 * SUM(placed) / COUNT(*), 1) AS placement_rate_pct
FROM students
GROUP BY cgpa_band;

DROP VIEW IF EXISTS vw_backlog_impact;
CREATE VIEW vw_backlog_impact AS
SELECT
    backlogs,
    COUNT(*) AS students,
    ROUND(100.0 * SUM(placed) / COUNT(*), 1) AS placement_rate_pct
FROM students
GROUP BY backlogs;

DROP VIEW IF EXISTS vw_skill_gap;
CREATE VIEW vw_skill_gap AS
SELECT 'coding_score' AS skill,
       ROUND(AVG(CASE WHEN placed = 1 THEN coding_score END), 1) AS placed_avg,
       ROUND(AVG(CASE WHEN placed = 0 THEN coding_score END), 1) AS not_placed_avg
FROM students
UNION ALL
SELECT 'aptitude_score',
       ROUND(AVG(CASE WHEN placed = 1 THEN aptitude_score END), 1),
       ROUND(AVG(CASE WHEN placed = 0 THEN aptitude_score END), 1)
FROM students
UNION ALL
SELECT 'communication_score',
       ROUND(AVG(CASE WHEN placed = 1 THEN communication_score END), 1),
       ROUND(AVG(CASE WHEN placed = 0 THEN communication_score END), 1)
FROM students
UNION ALL
SELECT 'data_tools_score',
       ROUND(AVG(CASE WHEN placed = 1 THEN data_tools_score END), 1),
       ROUND(AVG(CASE WHEN placed = 0 THEN data_tools_score END), 1)
FROM students
UNION ALL
SELECT 'mock_interviews',
       ROUND(AVG(CASE WHEN placed = 1 THEN mock_interviews END), 1),
       ROUND(AVG(CASE WHEN placed = 0 THEN mock_interviews END), 1)
FROM students
UNION ALL
SELECT 'internships',
       ROUND(AVG(CASE WHEN placed = 1 THEN internships END), 1),
       ROUND(AVG(CASE WHEN placed = 0 THEN internships END), 1)
FROM students
UNION ALL
SELECT 'projects',
       ROUND(AVG(CASE WHEN placed = 1 THEN projects END), 1),
       ROUND(AVG(CASE WHEN placed = 0 THEN projects END), 1)
FROM students;

DROP VIEW IF EXISTS vw_sector_offers;
CREATE VIEW vw_sector_offers AS
SELECT
    c.sector,
    c.is_tech,
    COUNT(o.offer_id) AS offers,
    ROUND(100.0 * COUNT(o.offer_id) / (SELECT COUNT(*) FROM offers), 1) AS share_of_offers_pct,
    ROUND(AVG(o.package_lpa), 2) AS avg_package_lpa
FROM companies c
LEFT JOIN offers o ON o.company_id = c.company_id
GROUP BY c.sector, c.is_tech;

DROP VIEW IF EXISTS vw_non_tech_share;
CREATE VIEW vw_non_tech_share AS
SELECT
    ROUND(100.0 * SUM(CASE WHEN c.is_tech = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS non_tech_offer_pct,
    ROUND(AVG(CASE WHEN c.is_tech = 0 THEN o.package_lpa END), 2) AS non_tech_avg_package_lpa,
    ROUND(AVG(CASE WHEN c.is_tech = 1 THEN o.package_lpa END), 2) AS tech_avg_package_lpa
FROM offers o
JOIN companies c ON c.company_id = o.company_id;

-- One row per student, with offer details when the student is placed.
-- This is the main table loaded into Power BI and Tableau.
-- Safe from double counting because offers has at most one row per student.
DROP VIEW IF EXISTS vw_student_flat;
CREATE VIEW vw_student_flat AS
SELECT
    s.student_id,
    s.branch,
    s.cgpa,
    CASE
        WHEN s.cgpa < 7 THEN '1. Below 7'
        WHEN s.cgpa < 8 THEN '2. 7 to under 8'
        WHEN s.cgpa < 9 THEN '3. 8 to under 9'
        ELSE '4. 9 and above'
    END AS cgpa_band,
    s.backlogs,
    s.internships,
    s.projects,
    s.certifications,
    s.coding_score,
    s.aptitude_score,
    s.communication_score,
    s.mock_interviews,
    s.data_tools_score,
    s.placed,
    CASE WHEN s.placed = 1 THEN 'Placed' ELSE 'Not placed' END AS placement_status,
    c.company_name,
    c.sector,
    c.is_tech,
    CASE WHEN c.is_tech = 1 THEN 'Tech'
         WHEN c.is_tech = 0 THEN 'Non-tech' END AS company_type,
    o.package_lpa
FROM students s
LEFT JOIN offers o    ON o.student_id = s.student_id
LEFT JOIN companies c ON c.company_id = o.company_id;

-- Author: Anveshaa Kesharwaani
-- Core tables for the placement database (SQLite).

CREATE TABLE students (
    student_id          INTEGER PRIMARY KEY,
    branch              TEXT NOT NULL,
    cgpa                REAL CHECK (cgpa BETWEEN 0 AND 10),
    backlogs            INTEGER CHECK (backlogs >= 0),
    internships         INTEGER CHECK (internships >= 0),
    projects            INTEGER CHECK (projects >= 0),
    certifications      INTEGER CHECK (certifications >= 0),
    coding_score        REAL CHECK (coding_score BETWEEN 0 AND 100),
    aptitude_score      REAL CHECK (aptitude_score BETWEEN 0 AND 100),
    communication_score REAL CHECK (communication_score BETWEEN 0 AND 100),
    mock_interviews     INTEGER CHECK (mock_interviews >= 0),
    data_tools_score    REAL CHECK (data_tools_score BETWEEN 0 AND 100),
    placed              INTEGER NOT NULL CHECK (placed IN (0, 1))
);

CREATE TABLE companies (
    company_id   INTEGER PRIMARY KEY,
    company_name TEXT NOT NULL,
    sector       TEXT NOT NULL,
    is_tech      INTEGER NOT NULL CHECK (is_tech IN (0, 1))
);

CREATE TABLE offers (
    offer_id    INTEGER PRIMARY KEY,
    student_id  INTEGER NOT NULL REFERENCES students(student_id),
    company_id  INTEGER NOT NULL REFERENCES companies(company_id),
    package_lpa REAL NOT NULL CHECK (package_lpa > 0)
);

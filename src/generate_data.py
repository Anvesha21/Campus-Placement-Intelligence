"""Author: Anveshaa Kesharwaani

Generate a synthetic college placement dataset: students, companies, offers.

Everything here is fictional. The placement rule below is a made-up model used
to create realistic-looking data. It is NOT evidence about any real college.
No names, gender, caste, religion, address, or contact fields are generated.
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 2026
N_STUDENTS = 1200
DATA_DIR = Path("data")

BRANCHES = ["CSE", "ECE", "IT", "EE", "ME"]
BRANCH_PROBS = [0.30, 0.25, 0.20, 0.10, 0.15]
BRANCH_EFFECT = {"CSE": 0.40, "ECE": 0.10, "IT": 0.30, "EE": 0.00, "ME": -0.20}
INTERCEPT = -0.2
SIGNAL_SCALE = 0.5

# (company_name, sector, is_tech). All company names are fictional.
COMPANIES = [
    ("Arcadia Software", "Tech Product", 1),
    ("Nimbus Cloud Labs", "Tech Product", 1),
    ("Vertex IT Services", "IT Services", 1),
    ("Quantum Insights", "Analytics", 1),
    ("Helix Fintech", "Fintech", 1),
    ("Kestrel Consulting", "Consulting", 0),
    ("Bharat Motors", "Manufacturing", 0),
    ("Sunrise FMCG", "FMCG", 0),
    ("Lotus Retail Group", "Retail", 0),
    ("Prime Infra Builders", "Infrastructure", 0),
]

# Typical package per company in LPA (fictional).
BASE_PACKAGE = [14.0, 16.0, 5.5, 9.0, 10.0, 8.0, 6.0, 6.5, 4.5, 5.0]

# How often each company recruits from each branch (relative weights).
COMPANY_WEIGHTS = {
    "CSE": [3, 3, 3, 2, 2, 1, 0.5, 0.5, 0.5, 0.5],
    "ECE": [1.5, 1.5, 3, 1, 1, 1, 1.5, 1, 1, 1],
    "IT": [3, 2, 3, 2, 2, 1, 0.5, 0.5, 0.5, 0.5],
    "EE": [0.5, 0.5, 2, 0.5, 0.5, 1.5, 2, 1, 1, 2],
    "ME": [0.3, 0.3, 1.5, 0.3, 0.3, 2, 3, 2, 1.5, 2.5],
}


def generate(n: int = N_STUDENTS, seed: int = SEED):
    """Return (students, companies, offers) as DataFrames. Same seed, same data."""
    rng = np.random.default_rng(seed)

    branch = rng.choice(BRANCHES, size=n, p=BRANCH_PROBS)
    cgpa = np.clip(rng.normal(7.6, 0.9, n), 5.0, 10.0).round(2)
    backlogs = np.clip(rng.poisson(0.4, n), 0, 4)
    internships = np.clip(rng.poisson(0.9, n), 0, 4)
    projects = np.clip(rng.poisson(2.0, n), 0, 8)
    certifications = np.clip(rng.poisson(1.5, n), 0, 8)
    coding = np.clip(rng.normal(55, 18, n), 0, 100).round(1)
    aptitude = np.clip(rng.normal(60, 15, n), 0, 100).round(1)
    communication = np.clip(rng.normal(62, 15, n), 0, 100).round(1)
    mock = np.clip(rng.poisson(2.0, n), 0, 10)
    data_tools = np.clip(rng.normal(45, 20, n), 0, 100).round(1)

    branch_effect = np.array([BRANCH_EFFECT[b] for b in branch])
    signal = (
        0.9 * (cgpa - 7.5)
        - 0.8 * backlogs
        + 0.45 * internships
        + 0.15 * projects
        + 0.10 * certifications
        + 0.03 * (coding - 55)
        + 0.02 * (aptitude - 60)
        + 0.025 * (communication - 62)
        + 0.10 * mock
        + 0.012 * (data_tools - 45)
        + 0.60 * (coding >= 70)  # strong coders get an extra boost (non-linear)
        + branch_effect
    )
    # Scaling the signal keeps probabilities away from 0% and 100% for
    # extreme profiles, so the demo does not look overconfident.
    z = INTERCEPT + SIGNAL_SCALE * signal
    prob = 1 / (1 + np.exp(-z))
    placed = (rng.random(n) < prob).astype(int)

    students = pd.DataFrame(
        {
            "student_id": np.arange(1, n + 1),
            "branch": branch,
            "cgpa": cgpa,
            "backlogs": backlogs,
            "internships": internships,
            "projects": projects,
            "certifications": certifications,
            "coding_score": coding,
            "aptitude_score": aptitude,
            "communication_score": communication,
            "mock_interviews": mock,
            "data_tools_score": data_tools,
            "placed": placed,
        }
    )

    offer_rows = []
    for i in np.flatnonzero(placed):
        w = np.array(COMPANY_WEIGHTS[branch[i]], dtype=float)
        c = int(rng.choice(len(COMPANIES), p=w / w.sum()))
        package = BASE_PACKAGE[c] * rng.uniform(0.85, 1.25) * (1 + (coding[i] - 50) / 200)
        offer_rows.append(
            {"student_id": int(i + 1), "company_id": c + 1, "package_lpa": round(float(package), 2)}
        )
    offers = pd.DataFrame(offer_rows, columns=["student_id", "company_id", "package_lpa"])
    offers.insert(0, "offer_id", np.arange(1, len(offers) + 1))

    companies = pd.DataFrame(COMPANIES, columns=["company_name", "sector", "is_tech"])
    companies.insert(0, "company_id", np.arange(1, len(companies) + 1))

    return students, companies, offers


def save_csvs(students, companies, offers, out_dir=DATA_DIR):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    students.to_csv(out_dir / "students.csv", index=False)
    companies.to_csv(out_dir / "companies.csv", index=False)
    offers.to_csv(out_dir / "offers.csv", index=False)


def main():
    students, companies, offers = generate()
    save_csvs(students, companies, offers)
    rate = students["placed"].mean() * 100
    print(f"Generated {len(students)} students, {len(offers)} offers, placement rate {rate:.1f}%")


if __name__ == "__main__":
    main()

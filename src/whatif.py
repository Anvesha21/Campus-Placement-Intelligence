"""Author: Anveshaa Kesharwaani

What-if simulator: change one thing about a student and see how the model's
placement probability moves.

Example: "What if coding score goes up by 10 points?" The student's row is
copied, the one value is changed, and the saved model scores both rows.

This shows how the MODEL responds. It is not proof that the change will cause
an offer (correlation, not causation).
"""
import pandas as pd

from src.features import to_matrix

# (label, feature, change)
ACTIONS = [
    ("Raise coding score by 10 points", "coding_score", 10),
    ("Raise aptitude score by 10 points", "aptitude_score", 10),
    ("Raise communication score by 10 points", "communication_score", 10),
    ("Raise Excel / SQL / Power BI score by 10 points", "data_tools_score", 10),
    ("Do 2 more mock interviews", "mock_interviews", 2),
    ("Complete 1 more internship", "internships", 1),
    ("Finish 1 more project", "projects", 1),
    ("Earn 1 more certification", "certifications", 1),
    ("Clear 1 backlog", "backlogs", -1),
]

# Allowed range per feature, same as the sliders in app.py.
LIMITS = {
    "coding_score": (0, 100),
    "aptitude_score": (0, 100),
    "communication_score": (0, 100),
    "data_tools_score": (0, 100),
    "mock_interviews": (0, 10),
    "internships": (0, 4),
    "projects": (0, 8),
    "certifications": (0, 8),
    "backlogs": (0, 4),
}


def probability(bundle: dict, student: dict) -> float:
    """Model probability of placement for one student dict."""
    X = to_matrix(pd.DataFrame([student]))[bundle["features"]]
    return float(bundle["model"].predict_proba(X)[0, 1])


def _apply(student: dict, feature: str, change: float) -> dict:
    low, high = LIMITS[feature]
    changed = dict(student)
    changed[feature] = min(high, max(low, float(student[feature]) + change))
    return changed


def simulate(student: dict, bundle: dict) -> pd.DataFrame:
    """Try every action alone. Returns the actions that change something, best first."""
    base = probability(bundle, student)
    rows = []
    for label, feature, change in ACTIONS:
        changed = _apply(student, feature, change)
        if changed[feature] == float(student[feature]):
            continue  # already at the limit, nothing to try
        new = probability(bundle, changed)
        rows.append({
            "action": label,
            "new_probability": round(new, 3),
            "uplift_points": round((new - base) * 100, 1),
        })
    out = pd.DataFrame(rows, columns=["action", "new_probability", "uplift_points"])
    return out.sort_values("uplift_points", ascending=False).reset_index(drop=True)


def plan(student: dict, bundle: dict, steps: int = 3) -> pd.DataFrame:
    """Greedy plan: pick the best action, apply it, then pick the next best.

    Each action is used at most once. Uplifts are measured against the student
    AFTER the earlier steps, so the numbers add up to the combined change.
    """
    current = dict(student)
    used = set()
    rows = []
    for _ in range(steps):
        before = probability(bundle, current)
        best = None
        for label, feature, change in ACTIONS:
            if label in used:
                continue
            changed = _apply(current, feature, change)
            if changed[feature] == float(current[feature]):
                continue
            gain = probability(bundle, changed) - before
            if best is None or gain > best[0]:
                best = (gain, label, changed)
        if best is None or best[0] <= 0:
            break
        gain, label, current = best
        used.add(label)
        rows.append({
            "step": len(rows) + 1,
            "action": label,
            "probability_after": round(before + gain, 3),
            "step_uplift_points": round(gain * 100, 1),
        })
    return pd.DataFrame(rows, columns=["step", "action", "probability_after", "step_uplift_points"])


def median_student(df: pd.DataFrame) -> dict:
    """A representative student: median of every numeric field, branch CSE."""
    cols = [c for c in df.columns if c not in ("student_id", "branch", "placed")]
    student = df[cols].median().round(1).to_dict()
    for k in ("backlogs", "internships", "projects", "certifications", "mock_interviews"):
        student[k] = int(round(student[k]))
    student["branch"] = "CSE"
    return student

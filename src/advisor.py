"""Author: Anveshaa Kesharwaani

Explain a student's placement chances and suggest what to work on first.

The advice is rule-based. It compares the student's numbers with the median
profile of placed students in the data, then points at the largest gaps in
things the student can change within a few months.

This is a descriptive comparison, not a causal claim. Fixing a gap does not
guarantee an offer.
"""
import pandas as pd

ADVICE = {
    "coding_score": "Coding test: solve 2 timed problems a day. SQL and Python both count for analytics roles.",
    "aptitude_score": "Aptitude: practise quantitative and logical reasoning for 30 minutes a day.",
    "communication_score": "Communication: record yourself answering 'Tell me about yourself' and cut filler words.",
    "data_tools_score": "Data tools: build one Excel dashboard and one SQL analysis you can explain line by line.",
    "mock_interviews": "Mock interviews: book at least 3 more practice rounds before applications open.",
    "internships": "Internships: apply to 2 short internships or live projects this semester.",
    "projects": "Projects: finish one project end to end and be ready to demo it.",
    "certifications": "Certifications: complete one free course with a certificate in your target skill.",
    "backlogs": "Backlogs: clear pending subjects first. Pending backlogs can block eligibility for some drives.",
}
ACTIONABLE = list(ADVICE)

MIN_GAP = 0.2  # in standard deviations; smaller gaps are ignored


def placed_profile(df: pd.DataFrame) -> pd.Series:
    """Median values of the actionable features among placed students."""
    return df.loc[df["placed"] == 1, ACTIONABLE].median()


def band(prob: float) -> str:
    if prob >= 0.70:
        return "Strong"
    if prob >= 0.40:
        return "Moderate"
    return "Needs work"


def advise(student: dict, df: pd.DataFrame, top_n: int = 3) -> list[str]:
    """Return up to top_n advice lines, largest gap first."""
    profile = placed_profile(df)
    spread = df[ACTIONABLE].std()

    gaps = []
    for feature in ACTIONABLE:
        value = float(student[feature])
        if feature == "backlogs":
            gap = (value - profile[feature]) / spread[feature]  # more backlogs is worse
        else:
            gap = (profile[feature] - value) / spread[feature]
        if gap > MIN_GAP:
            gaps.append((gap, feature))

    gaps.sort(reverse=True)
    return [ADVICE[feature] for _, feature in gaps[:top_n]]

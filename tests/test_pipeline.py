"""Author: Anveshaa Kesharwaani

Basic checks for the pipeline. Run from the project root:
    python -m pytest -q
"""
import sqlite3

from src.build_database import build
from src.features import FEATURE_COLUMNS, to_matrix
from src.generate_data import generate, save_csvs


def test_no_personal_identifiers_in_data():
    students, companies, offers = generate(n=300, seed=1)
    banned = {"name", "gender", "caste", "religion", "address", "phone", "email"}
    assert banned.isdisjoint(students.columns)
    assert banned.isdisjoint(companies.columns)
    assert banned.isdisjoint(offers.columns)


def test_placement_rate_is_plausible():
    students, _, _ = generate(n=1200, seed=2026)
    rate = students["placed"].mean()
    assert 0.35 <= rate <= 0.85


def test_every_placed_student_has_exactly_one_offer():
    students, _, offers = generate(n=500, seed=7)
    placed_ids = set(students.loc[students["placed"] == 1, "student_id"])
    offer_ids = offers["student_id"].tolist()
    assert placed_ids == set(offer_ids)
    assert len(offer_ids) == len(set(offer_ids))


def test_generation_is_reproducible():
    a, _, _ = generate(n=100, seed=99)
    b, _, _ = generate(n=100, seed=99)
    assert a.equals(b)


def test_feature_matrix_has_expected_columns():
    students, _, _ = generate(n=50, seed=3)
    X = to_matrix(students)
    assert list(X.columns) == FEATURE_COLUMNS
    assert len(X) == 50


def test_database_views_return_rows(tmp_path):
    students, companies, offers = generate(n=300, seed=5)
    save_csvs(students, companies, offers, out_dir=tmp_path)
    db = tmp_path / "test.db"
    counts = build(db_path=db, data_dir=tmp_path)
    assert counts["students"] == 300

    conn = sqlite3.connect(db)
    try:
        for view in [
            "vw_branch_summary",
            "vw_cgpa_band",
            "vw_backlog_impact",
            "vw_skill_gap",
            "vw_sector_offers",
            "vw_non_tech_share",
        ]:
            n = conn.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]
            assert n > 0, f"{view} returned no rows"
    finally:
        conn.close()


def test_bi_export_has_one_scored_row_per_student(tmp_path):
    import pandas as pd

    from src.export_bi import export
    from src.images import make_architecture, make_dashboard_preview
    from src.train_model import train

    students, companies, offers = generate(n=300, seed=11)
    save_csvs(students, companies, offers, out_dir=tmp_path)
    db = tmp_path / "t.db"
    build(db_path=db, data_dir=tmp_path)
    train(db_path=db, model_path=tmp_path / "m.joblib", report_dir=tmp_path / "reports")
    written = export(db_path=db, model_path=tmp_path / "m.joblib", bi_dir=tmp_path / "bi")
    assert written["students_scored.csv"] == 300

    scored = pd.read_csv(tmp_path / "bi" / "students_scored.csv")
    assert len(scored) == 300
    assert scored["student_id"].is_unique
    assert scored["ai_probability"].between(0, 1).all()
    assert scored["top_advice"].notna().all()
    assert scored.loc[scored["placed"] == 1, "package_lpa"].notna().all()
    assert scored.loc[scored["placed"] == 0, "package_lpa"].isna().all()

    assert make_architecture(report_dir=tmp_path / "img").stat().st_size > 0
    assert make_dashboard_preview(bi_dir=tmp_path / "bi", report_dir=tmp_path / "img").stat().st_size > 0


def _small_project(tmp_path, n=400, seed=21):
    from src.train_model import train

    students, companies, offers = generate(n=n, seed=seed)
    save_csvs(students, companies, offers, out_dir=tmp_path)
    db = tmp_path / "v2.db"
    build(db_path=db, data_dir=tmp_path)
    train(db_path=db, model_path=tmp_path / "m.joblib", report_dir=tmp_path / "reports")
    return db, tmp_path / "m.joblib"


def test_advanced_views_return_sensible_rows(tmp_path):
    db, _ = _small_project(tmp_path)
    conn = sqlite3.connect(db)
    try:
        funnel = conn.execute("SELECT students FROM vw_funnel ORDER BY stage_no").fetchall()
        counts = [r[0] for r in funnel]
        assert counts[0] == 400
        assert counts == sorted(counts, reverse=True)  # each stage can only shrink

        quartiles = conn.execute("SELECT offers FROM vw_package_quartiles").fetchall()
        assert len(quartiles) == 4
        assert max(q[0] for q in quartiles) - min(q[0] for q in quartiles) <= 1

        last = conn.execute(
            "SELECT cumulative_pct FROM vw_package_bands ORDER BY package_band DESC LIMIT 1"
        ).fetchone()[0]
        assert last == 100.0

        ranks = conn.execute("SELECT rate_rank FROM vw_branch_rank").fetchall()
        assert 1 in [r[0] for r in ranks]
    finally:
        conn.close()


def test_whatif_actions_are_valid_and_sorted(tmp_path):
    import joblib
    import pandas as pd

    from src.whatif import median_student, plan, simulate

    db, model_path = _small_project(tmp_path)
    bundle = joblib.load(model_path)
    students = pd.read_sql("SELECT * FROM students", sqlite3.connect(db))
    student = median_student(students)

    sim = simulate(student, bundle)
    assert not sim.empty
    assert sim["new_probability"].between(0, 1).all()
    assert sim["uplift_points"].is_monotonic_decreasing

    steps = plan(student, bundle, steps=3)
    assert len(steps) <= 3
    assert steps["action"].is_unique


def test_whatif_skips_actions_at_the_limit(tmp_path):
    import joblib

    from src.whatif import simulate

    _, model_path = _small_project(tmp_path)
    bundle = joblib.load(model_path)
    maxed = {
        "branch": "CSE", "cgpa": 8.0, "backlogs": 0, "internships": 4, "projects": 8,
        "certifications": 8, "coding_score": 100.0, "aptitude_score": 100.0,
        "communication_score": 100.0, "mock_interviews": 10, "data_tools_score": 100.0,
    }
    assert simulate(maxed, bundle).empty  # nothing left to improve


def test_html_dashboard_is_built_and_self_contained(tmp_path):
    from src.export_bi import export
    from src.html_dashboard import build_dashboard

    db, model_path = _small_project(tmp_path, n=300, seed=22)
    export(db_path=db, model_path=model_path, bi_dir=tmp_path / "bi")
    path = build_dashboard(bi_dir=tmp_path / "bi", out_dir=tmp_path / "dash")
    html = path.read_text(encoding="utf-8")
    assert "Anveshaa Kesharwaani" in html
    assert "const DATA = [" in html
    assert "http://" not in html and "https://" not in html  # works offline


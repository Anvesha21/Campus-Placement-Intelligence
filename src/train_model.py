"""Author: Anveshaa Kesharwaani

Train two models, compare them, and save the better one.

- Logistic regression: simple and explainable. Its coefficients show which
  factors push placement up or down.
- Random forest: can learn non-linear patterns, such as a threshold effect.

The best model is chosen by cross-validated ROC-AUC on the TRAINING split only.
The test split is used once, at the end, for the reported numbers.
"""
import json
import sqlite3
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.features import FEATURE_COLUMNS, TARGET, to_matrix

DB_PATH = Path("data/placement.db")
MODEL_PATH = Path("models/placement_model.joblib")
REPORT_DIR = Path("reports")
RANDOM_STATE = 42


def load_students(db_path=DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    try:
        return pd.read_sql("SELECT * FROM students", conn)
    finally:
        conn.close()


def candidate_models():
    return {
        "logistic_regression": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=1000)
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300, max_depth=6, min_samples_leaf=5, random_state=RANDOM_STATE
        ),
    }


def train(db_path=DB_PATH, model_path=MODEL_PATH, report_dir=REPORT_DIR) -> dict:
    df = load_students(db_path)
    X = to_matrix(df)
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=RANDOM_STATE
    )

    results, fitted = {}, {}
    for name, model in candidate_models().items():
        cv_auc = cross_val_score(model, X_train, y_train, cv=5, scoring="roc_auc")
        model.fit(X_train, y_train)

        proba = model.predict_proba(X_test)[:, 1]
        pred = (proba >= 0.5).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()

        results[name] = {
            "cv_roc_auc_mean": round(float(cv_auc.mean()), 3),
            "cv_roc_auc_std": round(float(cv_auc.std()), 3),
            "test_roc_auc": round(float(roc_auc_score(y_test, proba)), 3),
            "test_accuracy": round(float(accuracy_score(y_test, pred)), 3),
            "test_precision": round(float(precision_score(y_test, pred)), 3),
            "test_recall": round(float(recall_score(y_test, pred)), 3),
            "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        }
        fitted[name] = model

    # Prefer the simpler, explainable model unless another model is clearly
    # better (more than 0.01 cross-validated AUC). Small gaps are noise.
    best_name = "logistic_regression"
    challenger = max(results, key=lambda n: results[n]["cv_roc_auc_mean"])
    gain = results[challenger]["cv_roc_auc_mean"] - results["logistic_regression"]["cv_roc_auc_mean"]
    if gain > 0.01:
        best_name = challenger
    best = fitted[best_name]

    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model": best, "model_name": best_name, "features": FEATURE_COLUMNS},
        model_path,
    )

    # Explainability: coefficients from the logistic model (inputs are standardized,
    # so the sizes are comparable). Saved even when the forest wins.
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    lr = fitted["logistic_regression"].named_steps["logisticregression"]
    drivers = pd.DataFrame({"feature": FEATURE_COLUMNS, "coefficient": lr.coef_[0].round(3)})
    drivers = drivers.reindex(drivers.coefficient.abs().sort_values(ascending=False).index)
    drivers.to_csv(report_dir / "feature_drivers.csv", index=False)

    metrics = {
        "best_model": best_name,
        "rows_total": int(len(df)),
        "rows_train": int(len(X_train)),
        "rows_test": int(len(X_test)),
        "placement_rate_pct": round(float(y.mean()) * 100, 1),
        "models": results,
    }
    (report_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    m = train()
    print("Best model:", m["best_model"])
    for name, r in m["models"].items():
        print(f"  {name}: CV AUC {r['cv_roc_auc_mean']}, test AUC {r['test_roc_auc']}, "
              f"accuracy {r['test_accuracy']}")

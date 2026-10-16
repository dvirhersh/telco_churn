"""Validate step: refit baseline and champion on all of train.csv, score once on holdout.csv.

Run from the repo root:  python work/delivery/holdout_validation.py
This is the only script that reads holdout.csv. It refuses to run again once
holdout_metrics.json exists, so the holdout is read for evaluation exactly once.
"""
import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "work" / "modeling"))
import baseline  # noqa: E402  fixed baseline pipeline (independent of the search)
import fitness  # noqa: E402  champion decoding + pipeline, as run on Earth

HERE = Path(__file__).resolve().parent
TRAIN = ROOT / "work" / "exploration" / "train.csv"
HOLDOUT = ROOT / "work" / "exploration" / "holdout.csv"
CHAMPION = ROOT / "work" / "optimization" / "champion.json"
OUT = HERE / "holdout_metrics.json"
TARGET, THRESHOLD = "Churn Value", 0.5


def metrics(y, proba) -> dict:
    pred = (proba >= THRESHOLD).astype(int)
    tn, fp, fn, tp = (int(v) for v in confusion_matrix(y, pred, labels=[0, 1]).ravel())
    return {"f1": round(float(f1_score(y, pred, zero_division=0)), 4),
            "precision": round(float(precision_score(y, pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y, pred, zero_division=0)), 4),
            "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp}}


def main() -> None:
    if OUT.exists():
        raise SystemExit(f"{OUT.name} already exists; the holdout has been scored. Not re-reading it.")

    champion = json.loads(CHAMPION.read_text())
    train = pd.read_csv(TRAIN)
    X, y = train.drop(columns=[TARGET]), train[TARGET]
    num_cols = X.select_dtypes("number").columns.tolist()
    cat_cols = X.select_dtypes(exclude="number").columns.tolist()

    cfg = fitness.decode(champion["chromosome"])
    models = {
        "baseline": baseline.build_pipeline(num_cols, cat_cols),
        "champion": fitness.build_pipeline(cfg, num_cols, cat_cols),
    }
    for model in models.values():
        model.fit(X, y)  # refit on all of train.csv

    # Single holdout read
    holdout = pd.read_csv(HOLDOUT)
    X_h, y_h = holdout.drop(columns=[TARGET]), holdout[TARGET]
    assert list(X_h.columns) == list(X.columns), "holdout columns differ from train"

    results = {name: metrics(y_h, m.predict_proba(X_h)[:, 1]) for name, m in models.items()}
    delta = round(results["champion"]["f1"] - results["baseline"]["f1"], 4)
    report = {
        "protocol": "refit on all of train.csv (5634 rows), score once on holdout.csv, threshold 0.5",
        "holdout_rows": len(holdout),
        "experiment_id": champion["experiment_id"],
        "champion_settings": cfg,
        "champion_validation_f1": round(champion["fitness_f1_validation"], 4),
        "baseline_validation_f1": json.loads((ROOT / "work" / "modeling" / "baseline_validation.json")
                                             .read_text())["f1"],
        "holdout": results,
        "holdout_f1_delta_champion_minus_baseline": delta,
        "prefer_champion": delta >= 0,
    }
    OUT.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

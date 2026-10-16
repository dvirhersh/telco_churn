"""Fixed baseline: sklearn logistic pipeline, F1 on a validation cut of train.csv.

Run from the repo root:  python work/modeling/baseline.py
Reads only work/exploration/train.csv. holdout.csv is never opened.
"""
import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

HERE = Path(__file__).resolve().parent
TRAIN = HERE.parent / "exploration" / "train.csv"
TARGET, SEED, THRESHOLD = "Churn Value", 42, 0.5


def build_pipeline(num_cols, cat_cols) -> Pipeline:
    pre = ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                          ("scale", StandardScaler())]), num_cols),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="constant", fill_value="None")),
                          ("onehot", OneHotEncoder(handle_unknown="ignore"))]), cat_cols),
    ])
    return Pipeline([("pre", pre),
                     ("clf", LogisticRegression(max_iter=1000, random_state=SEED))])


def main() -> None:
    # "None" is a real category in Offer / Internet Type; the imputer restores it after CSV round-trip
    train = pd.read_csv(TRAIN)
    X, y = train.drop(columns=[TARGET]), train[TARGET]
    X_in, X_val, y_in, y_val = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEED)

    num_cols = X.select_dtypes("number").columns.tolist()
    cat_cols = X.select_dtypes(exclude="number").columns.tolist()
    model = build_pipeline(num_cols, cat_cols).fit(X_in, y_in)

    pred = (model.predict_proba(X_val)[:, 1] >= THRESHOLD).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_val, pred).ravel()
    result = {
        "split": "inner_train/validation from train.csv, stratified 80/20, seed 42",
        "inner_train_rows": len(X_in), "validation_rows": len(X_val),
        "threshold": THRESHOLD,
        "f1": round(f1_score(y_val, pred, zero_division=0), 4),
        "precision": round(precision_score(y_val, pred, zero_division=0), 4),
        "recall": round(recall_score(y_val, pred, zero_division=0), 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "model": "LogisticRegression(max_iter=1000), median+scale numerics, one-hot categoricals",
    }
    print(json.dumps(result, indent=2))
    (HERE / "baseline_validation.json").write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

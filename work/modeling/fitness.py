"""Earth fitness for Workshop 1: logistic regression, F1 on validation.

Self-contained single file (Earth runs one fitness.py per worker).
Data: the uploaded train.csv only. inner_train / validation is the same
stratified 80/20 cut (seed 42) the baseline uses. holdout.csv is never uploaded.
Genes and decoding rules: work/modeling/formulation.md.
"""
import glob
import math
import os
import warnings
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from pydantic import BaseModel
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (MinMaxScaler, OneHotEncoder, RobustScaler,
                                   StandardScaler)

TARGET = "Churn Value"
SEED = 42
THRESHOLD = 0.5
MAX_ITER = 1000
FLOOR = 1e-9  # Earth needs a strictly positive, finite score

SCALERS = {"none": None, "standard": StandardScaler, "minmax": MinMaxScaler,
           "robust": RobustScaler}
PENALTY_SOLVER = {"l2_lbfgs": ("l2", "lbfgs"), "l1_liblinear": ("l1", "liblinear"),
                  "elasticnet_saga": ("elasticnet", "saga")}
BASELINE = {"scaling_method": "standard", "imbalance_method": "none",
            "log10_C": 0.0, "penalty_solver": "l2_lbfgs", "l1_ratio": 0.5}


class FitnessCalculationResult(BaseModel):
    score: float
    scalars: Optional[Dict[str, Union[float, int]]] = None
    rows: Optional[Dict[str, List[Union[str, float, int]]]] = None


def _float(value, default, lo, hi):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(x):
        return default
    return min(max(x, lo), hi)


def decode(chromosome: Any) -> dict:
    """Chromosome → validated settings. Unknown or bad values fall back to the baseline."""
    node = chromosome if isinstance(chromosome, dict) else {}
    node = node.get("content", node)
    lr = node.get("logistic_regression") or {}
    lr = lr.get("content", lr) if isinstance(lr, dict) else {}

    scaling = node.get("scaling_method")
    imbalance = node.get("imbalance_method")
    penalty_solver = lr.get("penalty_solver")
    return {
        "scaling_method": scaling if scaling in SCALERS else BASELINE["scaling_method"],
        "imbalance_method": imbalance if imbalance in ("none", "class_weight_balanced")
        else BASELINE["imbalance_method"],
        "log10_C": _float(lr.get("log10_C"), BASELINE["log10_C"], -3.0, 2.0),
        "penalty_solver": penalty_solver if penalty_solver in PENALTY_SOLVER
        else BASELINE["penalty_solver"],
        "l1_ratio": _float(lr.get("l1_ratio"), BASELINE["l1_ratio"], 0.0, 1.0),
    }


def build_pipeline(cfg: dict, num_cols, cat_cols) -> Pipeline:
    num_steps = [("impute", SimpleImputer(strategy="median"))]
    scaler = SCALERS[cfg["scaling_method"]]
    if scaler is not None:
        num_steps.append(("scale", scaler()))
    pre = ColumnTransformer([
        ("num", Pipeline(num_steps), num_cols),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="constant", fill_value="None")),
                          ("onehot", OneHotEncoder(handle_unknown="ignore"))]), cat_cols),
    ])
    penalty, solver = PENALTY_SOLVER[cfg["penalty_solver"]]
    clf_kwargs = {
        "C": 10.0 ** cfg["log10_C"],
        "penalty": penalty,
        "solver": solver,
        "max_iter": MAX_ITER,
        "random_state": SEED,
        "class_weight": "balanced" if cfg["imbalance_method"] == "class_weight_balanced" else None,
    }
    if penalty == "elasticnet":
        clf_kwargs["l1_ratio"] = cfg["l1_ratio"]
    return Pipeline([("pre", pre), ("clf", LogisticRegression(**clf_kwargs))])


class FitnessClass:
    def __init__(self, dataset_root: str):
        # Glob the CSV: Earth may rename the uploaded file
        csvs = sorted(glob.glob(os.path.join(dataset_root, "**", "*.csv"), recursive=True))
        if not csvs:
            raise FileNotFoundError(f"no CSV under {dataset_root}")
        train = pd.read_csv(csvs[0])
        if TARGET not in train.columns:
            raise ValueError(f"{csvs[0]} has no '{TARGET}' column")
        X, y = train.drop(columns=[TARGET]), train[TARGET].astype(int)
        self.X_in, self.X_val, self.y_in, self.y_val = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=SEED)
        self.num_cols = X.select_dtypes("number").columns.tolist()
        self.cat_cols = X.select_dtypes(exclude="number").columns.tolist()

    def calculate_fitness(self, chromosome: Any) -> FitnessCalculationResult:
        try:
            cfg = decode(chromosome)
            model = build_pipeline(cfg, self.num_cols, self.cat_cols)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # ConvergenceWarning for unscaled saga etc.
                model.fit(self.X_in, self.y_in)
                proba = model.predict_proba(self.X_val)[:, 1]
            pred = (proba >= THRESHOLD).astype(int)

            f1 = float(f1_score(self.y_val, pred, zero_division=0))
            precision = float(precision_score(self.y_val, pred, zero_division=0))
            recall = float(recall_score(self.y_val, pred, zero_division=0))
            tn, fp, fn, tp = (int(v) for v in confusion_matrix(self.y_val, pred, labels=[0, 1]).ravel())
            score = f1 if math.isfinite(f1) and f1 > FLOOR else FLOOR
            C = float(10.0 ** cfg["log10_C"])
            scalars = {"f1": f1, "precision": precision, "recall": recall, "C": C,
                       "tn": tn, "fp": fp, "fn": fn, "tp": tp}
            rows = {"setting": ["scaling_method", "imbalance_method", "penalty_solver"],
                    "value": [cfg["scaling_method"], cfg["imbalance_method"], cfg["penalty_solver"]]}
        except Exception as exc:
            print(f"fitness error: {type(exc).__name__}: {exc}")
            score = FLOOR
            scalars = {"error": 1}
            rows = None
        return FitnessCalculationResult(score=score, scalars=scalars, rows=rows)

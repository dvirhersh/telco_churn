"""Fitness for the Telco churn retention-call problem (matches earth/chromosome.yaml).

Decision: each month the retention team calls the 400 customers most likely to churn.
Score: the course hit@400. Over 5 stratified folds (seed 42), each validation fold gets
400 / 5 = 80 calls, so the score is the mean hit rate among the top 80 of each fold.
This reproduces the course numbers (logistic regression about 0.76, gentle boosting
about 0.81, random list about 0.27).
Per-fold scores and their standard deviation are reported as diagnostics; the GA
optimises the mean only. A chromosome that fails to score gets ERROR_SCORE instead of
raising, so one bad candidate cannot stop the run.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from pydantic import BaseModel
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, OrdinalEncoder, StandardScaler
from xgboost import XGBClassifier

# ---- CONTRACT: agreed plan -----------------------------------------------------------
TRAIN_ASSET = "train_clean.csv"
TEST_IDS_ASSET = "test_ids.csv"   # optional: customers also in the test set are dropped
TARGET = "Churn"
POSITIVE_CLASS = "Yes"
ID_COLUMN = "customerID"

# Fixed, ordered feature list -- must match feature_mask gene by position.
FEATURES = [
    "gender", "SeniorCitizen", "Partner", "Dependents", "tenure",
    "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity",
    "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV",
    "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod",
    "MonthlyCharges", "TotalCharges",
]
NUMERIC_FEATURES = {"tenure", "MonthlyCharges", "TotalCharges"}
CATEGORICAL_FEATURES = set(FEATURES) - NUMERIC_FEATURES
# Ordinal encoding: Contract has a real order; the rest get a fixed alphabetical order.
CONTRACT_ORDER = ["Month-to-month", "One year", "Two year"]

SEED = 42
CV_FOLDS = 5
CAPACITY = 400                      # calls per month
TOP_K = CAPACITY // CV_FOLDS        # 80 calls per validation fold
MODEL_FAMILIES = ("logistic_regression", "random_forest", "xgboost")
SCALERS = ("none", "standard", "minmax")
ENCODINGS = ("onehot", "ordinal")
CLASS_WEIGHTS = ("none", "balanced")
ERROR_SCORE = 1e-9                  # Earth needs a finite, strictly positive score
# ----------------------------------------------------------------------------------------


class FitnessCalculationResult(BaseModel):
    score: float
    scalars: dict[str, float | int | dict[str, float | int]] | None = None
    rows: dict[str, list[str | float | int]] | None = None


def asset_path(dataset_root: str, name: str) -> Path:
    # Earth copies every asset of the dataset into dataset_root (a relative path) before the run.
    path = Path(dataset_root) / name
    if not path.is_file():
        present = sorted(str(p.relative_to(dataset_root)) for p in Path(dataset_root).rglob("*") if p.is_file())
        raise FileNotFoundError(f"Asset {name!r} is not in the dataset; it holds {present}")
    return path


def load_table(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = [column for column in [*FEATURES, TARGET, ID_COLUMN] if column not in frame.columns]
    if missing:
        raise ValueError(f"{path.name} lacks required columns {missing}")
    return frame


def drop_test_customers(frame: pd.DataFrame, dataset_root: str) -> pd.DataFrame:
    # train_clean.csv still holds the 10 customers who are also in the test set.
    path = Path(dataset_root) / TEST_IDS_ASSET
    if not path.is_file():
        return frame
    test_ids = set(pd.read_csv(path)[ID_COLUMN])
    return frame[~frame[ID_COLUMN].isin(test_ids)]


def choice(genes: dict, name: str, allowed: tuple) -> str:
    value = str(genes[name])
    if value not in allowed:
        raise ValueError(f"{name}={value!r} is outside {allowed}")
    return value


def decode_mask(genes: dict) -> list[str]:
    mask = [bool(flag) for flag in genes["feature_mask"]]
    if len(mask) != len(FEATURES):
        raise ValueError(f"feature_mask has {len(mask)} flags for {len(FEATURES)} features")
    return [name for name, keep in zip(FEATURES, mask) if keep]


def build_scaler(genes: dict):
    scaler = choice(genes, "scaler", SCALERS)
    if scaler == "standard":
        return StandardScaler()
    if scaler == "minmax":
        return MinMaxScaler()
    return "passthrough"


def build_encoder(genes: dict, categorical: list[str], categories: dict[str, list]):
    if choice(genes, "encoding", ENCODINGS) == "onehot":
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    return OrdinalEncoder(
        categories=[categories[name] for name in categorical],
        handle_unknown="use_encoded_value", unknown_value=-1,
    )


def build_model(genes: dict, y_fit: pd.Series):
    family = choice(genes, "model_family", MODEL_FAMILIES)
    balanced = choice(genes, "class_weight", CLASS_WEIGHTS) == "balanced"

    if family == "logistic_regression":
        model = LogisticRegression(
            C=float(10 ** float(genes["lr_C_exponent"])),
            penalty=str(genes["lr_penalty"]), solver="liblinear",
            class_weight="balanced" if balanced else None, max_iter=1000, random_state=SEED,
        )
    elif family == "random_forest":
        max_depth = None if bool(genes["rf_max_depth_unbounded"]) else int(genes["rf_max_depth_value"])
        model = RandomForestClassifier(
            n_estimators=int(genes["rf_n_estimators"]), max_depth=max_depth,
            min_samples_leaf=max(1, round(10 ** float(genes["rf_min_samples_leaf_exponent"]))),
            max_features=str(genes["rf_max_features"]),
            class_weight="balanced" if balanced else None, random_state=SEED, n_jobs=1,
        )
    else:
        n_pos = int(y_fit.sum())
        model = XGBClassifier(
            n_estimators=int(genes["xgb_n_estimators"]),
            learning_rate=float(10 ** float(genes["xgb_learning_rate_exponent"])),
            max_depth=int(genes["xgb_max_depth"]),
            min_child_weight=float(10 ** float(genes["xgb_min_child_weight_exponent"])),
            subsample=float(genes["xgb_subsample"]),
            colsample_bytree=float(genes["xgb_colsample_bytree"]),
            scale_pos_weight=(len(y_fit) - n_pos) / max(n_pos, 1) if balanced else 1.0,
            eval_metric="logloss", tree_method="hist", random_state=SEED, n_jobs=1,
        )
    return family, model


def build_pipeline(genes, numeric, categorical, categories, y_fit) -> Pipeline:
    transformers = []
    if numeric:
        transformers.append(("num", build_scaler(genes), numeric))
    if categorical:
        transformers.append(("cat", build_encoder(genes, categorical, categories), categorical))
    preprocessor = ColumnTransformer(transformers, remainder="drop")
    _, model = build_model(genes, y_fit)
    return Pipeline([("prep", preprocessor), ("model", model)])


class FitnessClass:
    def __init__(self, dataset_root: str):
        frame = load_table(asset_path(dataset_root, TRAIN_ASSET))
        frame = drop_test_customers(frame, dataset_root).reset_index(drop=True)
        # Keep the file's row order: the folds below depend on it, as in the course.
        self.x = frame[FEATURES].copy()
        self.y = (frame[TARGET] == POSITIVE_CLASS).astype(int)
        self.categories = {
            name: (CONTRACT_ORDER if name == "Contract" else sorted(self.x[name].unique().tolist()))
            for name in CATEGORICAL_FEATURES
        }
        # Folds fixed once, with a fixed seed: every chromosome is scored on the same splits.
        self.folds = list(
            StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=SEED).split(self.x, self.y)
        )

    def calculate_fitness(self, chromosome: dict) -> FitnessCalculationResult:
        try:
            return self._score(chromosome)
        except Exception as exc:  # noqa: BLE001 -- Earth contract: never raise
            print(f"fitness error: {exc!r}")
            return FitnessCalculationResult(score=ERROR_SCORE, scalars={"error": 1})

    def _score(self, chromosome: dict) -> FitnessCalculationResult:
        genes = chromosome.get("content", chromosome)
        selected = decode_mask(genes)
        numeric = [name for name in selected if name in NUMERIC_FEATURES]
        categorical = [name for name in selected if name in CATEGORICAL_FEATURES]

        fold_hit_rates = []
        for train_index, valid_index in self.folds:
            x_fit, x_valid = self.x.iloc[train_index], self.x.iloc[valid_index]
            y_fit, y_valid = self.y.iloc[train_index], self.y.iloc[valid_index]
            k = min(TOP_K, len(y_valid))

            if selected:
                pipeline = build_pipeline(genes, numeric, categorical, self.categories, y_fit)
                pipeline.fit(x_fit[selected], y_fit)
                probability = pipeline.predict_proba(x_valid[selected])[:, 1]
            else:
                # No features selected: a real baseline (everyone gets the churn rate),
                # so the GA sees a random-list score of about 0.27, not a crash.
                baseline = DummyClassifier(strategy="prior").fit(np.zeros((len(y_fit), 1)), y_fit)
                probability = baseline.predict_proba(np.zeros((len(y_valid), 1)))[:, 1]

            top_k_positions = np.argsort(-probability, kind="stable")[:k]
            fold_hit_rates.append(float(y_valid.to_numpy()[top_k_positions].sum()) / k)

        score = float(np.mean(fold_hit_rates))
        scalars = {
            "hit_rate_at_400_mean": score,
            "hit_rate_at_400_std": float(np.std(fold_hit_rates)),
            "hit_rate_at_400_per_fold": {f"fold_{i}": rate for i, rate in enumerate(fold_hit_rates)},
            "selected_features": len(selected),
        }
        rows = {"model_family": [str(genes["model_family"])], "features": selected}
        return FitnessCalculationResult(score=score, scalars=scalars, rows=rows)

    def save_model(self):
        return None

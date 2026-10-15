"""Fitness skeleton for the term-deposit campaign. Copy it, then fill in the TODOs.

    cp earth/fitness_skeleton.py work/optimization/fitness.py

What Earth needs from this file:
  - a class FitnessClass(dataset_root) that loads the data once in __init__;
  - calculate_fitness(chromosome) -> FitnessCalculationResult, which never raises;
  - a score that is finite and > 0, where higher is better.

Every gene in your chromosome.yaml must be read somewhere in this file, and
every gene this file reads must exist in chromosome.yaml.
Check it locally before Earth:  python earth/check_local.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from pydantic import BaseModel
from sklearn.model_selection import StratifiedKFold, train_test_split

# ---- CONTRACT: your framing decisions, fixed for every chromosome ---------------------------
TRAIN_ASSET = "train.csv"           # the file run_search.py uploads (work/exploration/train.csv)
TARGET = "y"
POSITIVE_CLASS = "yes"
COST_PER_CALL = 10.0                # from PROJECT_BRIEF.md; never a gene
VALUE_PER_SUBSCRIPTION = 70.0       # from PROJECT_BRIEF.md; never a gene
SEED = 42
CV_FOLDS = 5
PICK_SIZE = 0.25                    # part of each training fold used to pick the share to call
ERROR_SCORE = 1e-9                  # Earth needs a finite score > 0

# TODO (Step 5): your feature boundary. Which columns may the model use?
# Leave out anything not known before the call. Group them if you want a gene
# that switches a whole group on or off.
FEATURE_GROUPS = {
    # "client": {"num": ["age"], "cat": ["job", "marital", ...]},
}
# ----------------------------------------------------------------------------------------------


class FitnessCalculationResult(BaseModel):
    score: float
    scalars: dict[str, float | int | dict[str, float | int]] | None = None
    rows: dict[str, list[str | float | int]] | None = None


def campaign_profit(y_true: np.ndarray, call: np.ndarray) -> float:
    """Profit of calling the clients where call is True.

    TODO (Step 6): VALUE_PER_SUBSCRIPTION for every subscriber you call,
    minus COST_PER_CALL for every call you make.
    """
    raise NotImplementedError


def call_top_share(probability: np.ndarray, share: float) -> np.ndarray:
    """Call the top `share` of clients by predicted probability (array of True/False)."""
    n = int(round(share * len(probability)))
    call = np.zeros(len(probability), dtype=bool)
    call[np.argsort(-probability, kind="stable")[:n]] = True
    return call


def best_call_share(probability: np.ndarray, y_true: np.ndarray) -> float:
    """The share of clients to call that makes the most profit on these clients.

    Called only with clients from the training part of a fold, never the
    validation fold.
    TODO (Step 6): rank the clients by probability, compute the profit of calling
    the top 1, top 2, ... clients, and return the best number as a share of
    len(probability). If no list makes a profit, return 0.0.
    """
    raise NotImplementedError


def build_pipeline(genes: dict, y_fit: np.ndarray):
    """Return (sklearn Pipeline, list of input columns) for one chromosome.

    TODO (Step 6): read the genes (model family, hyperparameters, feature
    groups, preprocessing choices) and build the pipeline. Use n_jobs=1 in
    every model: Earth gives each worker one CPU.
    """
    raise NotImplementedError


class FitnessClass:
    def __init__(self, dataset_root: str):
        path = Path(dataset_root) / TRAIN_ASSET
        if not path.is_file():
            present = sorted(p.name for p in Path(dataset_root).rglob("*") if p.is_file())
            raise FileNotFoundError(f"{TRAIN_ASSET} not in the dataset; it holds {present}")
        self.x = pd.read_csv(path)
        # TODO (Step 6, optional): derived columns your genes need, e.g. a flag for pdays == 999.
        self.y = (self.x[TARGET] == POSITIVE_CLASS).astype(int).to_numpy()
        # Folds are fixed once: every chromosome is scored on the same splits.
        self.folds = list(StratifiedKFold(CV_FOLDS, shuffle=True, random_state=SEED).split(self.x, self.y))
        # Inside each training part: (1 - PICK_SIZE) to fit, PICK_SIZE to pick the share to call.
        self.picks = [
            train_test_split(train_idx, test_size=PICK_SIZE, stratify=self.y[train_idx], random_state=SEED)
            for train_idx, _ in self.folds
        ]

    def calculate_fitness(self, chromosome: dict) -> FitnessCalculationResult:
        try:
            return self._score(chromosome.get("content", chromosome))
        except Exception as exc:  # noqa: BLE001 -- Earth contract: never raise
            print(f"fitness error: {exc!r}")
            return FitnessCalculationResult(score=ERROR_SCORE, scalars={"error": 1})

    def _score(self, genes: dict) -> FitnessCalculationResult:
        fold_profits, shares = [], []
        for (train_idx, valid_idx), (fit_idx, pick_idx) in zip(self.folds, self.picks):
            # 1. Pick how many to call, using the training part only.
            pipe, cols = build_pipeline(genes, self.y[fit_idx])
            pipe.fit(self.x.iloc[fit_idx][cols], self.y[fit_idx])
            share = best_call_share(pipe.predict_proba(self.x.iloc[pick_idx][cols])[:, 1], self.y[pick_idx])
            # 2. Refit on the whole training part, call that share of the validation fold.
            pipe, cols = build_pipeline(genes, self.y[train_idx])
            pipe.fit(self.x.iloc[train_idx][cols], self.y[train_idx])
            probability = pipe.predict_proba(self.x.iloc[valid_idx][cols])[:, 1]
            call = call_top_share(probability, share)
            fold_profits.append(campaign_profit(self.y[valid_idx], call) * 1000 / len(valid_idx))
            shares.append(share)

        # TODO (Step 6): turn profit into a score that is > 0 and where higher is
        # better. Profit can be negative, so you need a decision here; write it in
        # work/design.md. Keep the score roughly between 0 and 1.
        score = ...
        return FitnessCalculationResult(
            score=max(float(score), ERROR_SCORE),
            scalars={
                "profit_per_1000_mean": float(np.mean(fold_profits)),
                "profit_per_1000_std": float(np.std(fold_profits)),
                "profit_per_1000_per_fold": {f"fold_{i}": float(p) for i, p in enumerate(fold_profits)},
                "share_called": float(np.mean(shares)),
                # TODO (stretch): precision of the call list.
            },
        )

    def save_model(self):
        return None

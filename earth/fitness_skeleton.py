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
from sklearn.model_selection import StratifiedKFold

# ---- CONTRACT: your framing decisions, fixed for every chromosome ---------------------------
TRAIN_ASSET = "train.csv"           # the file run_search.py uploads (work/exploration/train.csv)
TARGET = "y"
POSITIVE_CLASS = "yes"
COST_PER_CALL = 10.0                # from PROJECT_BRIEF.md; never a gene
VALUE_PER_SUBSCRIPTION = 70.0       # from PROJECT_BRIEF.md; never a gene
SEED = 42
CV_FOLDS = 5
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


def call_list(probability: np.ndarray, genes: dict) -> np.ndarray:
    """Turn predicted probabilities into a call list (array of True/False).

    TODO (Step 6): implement the calling policy you wrote in work/design.md,
    for example "call everyone above a probability cut-off" or "call the top
    share of the list". If the policy has a parameter Earth may tune, read it
    from genes.
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

    def calculate_fitness(self, chromosome: dict) -> FitnessCalculationResult:
        try:
            return self._score(chromosome.get("content", chromosome))
        except Exception as exc:  # noqa: BLE001 -- Earth contract: never raise
            print(f"fitness error: {exc!r}")
            return FitnessCalculationResult(score=ERROR_SCORE, scalars={"error": 1})

    def _score(self, genes: dict) -> FitnessCalculationResult:
        fold_profits = []
        for train_idx, valid_idx in self.folds:
            pipe, cols = build_pipeline(genes, self.y[train_idx])
            pipe.fit(self.x.iloc[train_idx][cols], self.y[train_idx])
            probability = pipe.predict_proba(self.x.iloc[valid_idx][cols])[:, 1]
            call = call_list(probability, genes)
            fold_profits.append(campaign_profit(self.y[valid_idx], call) * 1000 / len(valid_idx))

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
                # TODO (stretch): share of clients called, precision of the call list.
            },
        )

    def save_model(self):
        return None

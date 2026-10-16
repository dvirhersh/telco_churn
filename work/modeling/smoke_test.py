"""Local smoke test for work/modeling/fitness.py.

Run from the repo root:  python work/modeling/smoke_test.py
Copies train.csv (only) into a temp dataset_root under a different name, to mimic
the Earth upload, then checks:
  1. the baseline chromosome reproduces the baseline validation F1
  2. a set of valid chromosomes all return a positive, finite score
  3. malformed chromosomes return the floor score instead of raising
"""
import json
import math
import random
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fitness import FitnessClass  # noqa: E402

TRAIN = HERE.parent / "exploration" / "train.csv"
BASELINE_JSON = HERE / "baseline_validation.json"


def chromo(scaling, imbalance, log10_C, penalty_solver, l1_ratio=0.5):
    return {"scaling_method": scaling, "imbalance_method": imbalance,
            "logistic_regression": {"log10_C": log10_C, "penalty_solver": penalty_solver,
                                    "l1_ratio": l1_ratio}}


def main() -> None:
    with tempfile.TemporaryDirectory() as root:
        shutil.copy(TRAIN, Path(root) / "uploaded_dataset.csv")
        fit = FitnessClass(root)

    # 1. baseline parity
    expected = json.loads(BASELINE_JSON.read_text())["f1"]
    got = fit.calculate_fitness(chromo("standard", "none", 0.0, "l2_lbfgs")).score
    print(f"baseline chromosome: F1 {got:.4f} (baseline.py: {expected})")
    assert abs(got - expected) < 1e-4, "fitness does not reproduce the baseline"

    # 2. corners + random valid chromosomes
    rng = random.Random(0)
    cases = [chromo(s, i, c, p, r)
             for s in ("none", "standard", "minmax", "robust")
             for i in ("none", "class_weight_balanced")
             for c, p, r in ((-3.0, "l1_liblinear", 0.5), (2.0, "elasticnet_saga", 1.0))]
    cases += [chromo(rng.choice(["none", "standard", "minmax", "robust"]),
                     rng.choice(["none", "class_weight_balanced"]),
                     rng.uniform(-3, 2),
                     rng.choice(["l2_lbfgs", "l1_liblinear", "elasticnet_saga"]),
                     rng.uniform(0, 1)) for _ in range(10)]
    t0, scores = time.time(), []
    for c in cases:
        r = fit.calculate_fitness(c)
        assert math.isfinite(r.score) and r.score > 0, (c, r)
        assert "error" not in (r.scalars or {}), (c, r)
        scores.append(r.score)
    per_call = (time.time() - t0) / len(cases)
    print(f"{len(cases)} valid chromosomes: F1 min {min(scores):.4f}, max {max(scores):.4f}, "
          f"{per_call:.2f}s per call")

    # 3. malformed input never raises
    for bad in (None, {}, {"scaling_method": 3, "logistic_regression": "x"},
                chromo("bogus", "bogus", float("nan"), "bogus", -5)):
        r = fit.calculate_fitness(bad)
        assert math.isfinite(r.score) and r.score > 0, (bad, r)
    print("malformed chromosomes: handled (fall back to baseline settings)")
    print("SMOKE TEST PASSED")


if __name__ == "__main__":
    main()

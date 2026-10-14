"""Local pre-flight check: does this chromosome + fitness pair run on your laptop?

Usage:
    python earth/check_local.py
    python earth/check_local.py --chromosome work/runs/run2/chromosome.yaml
    python earth/check_local.py --fitness work/runs/run3/fitness.py

Builds one sample chromosome per model family from the YAML (first enum value,
range minimums, all features on), runs FitnessClass on data/train_clean.csv +
data/test_ids.csv in a temporary folder, and checks every score is finite and
positive. Catches wrong feature_mask sizes, enum values the fitness does not
know, and broken fitness edits before you spend an Earth run on them.
No Earth calls.
"""

from __future__ import annotations

import argparse
import importlib.util
import math
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]
TRAIN_CSV = _REPO_ROOT / "data" / "train_clean.csv"
TEST_IDS_CSV = _REPO_ROOT / "data" / "test_ids.csv"
# Fitness modules return a tiny score (1e-9) instead of raising; treat it as a failure.
ERROR_SCORE_CEILING = 1e-6


def load_fitness_module(path: Path):
    spec = importlib.util.spec_from_file_location("fitness_under_check", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_gene(spec: dict):
    """A deterministic value for one gene definition."""
    kind = spec.get("type")
    if kind == "enum":
        return spec["values"][0]
    if kind in ("int", "float"):
        return spec["min_value"]
    if kind == "bool":
        return False
    if kind == "array":
        if (spec.get("item_definition") or {}).get("type") != "bool":
            raise ValueError("only bool arrays are supported by this check")
        return [True] * int(spec["max_size"])
    if kind == "dict":
        return {name: sample_gene(sub) for name, sub in (spec.get("content") or {}).items()}
    raise ValueError(f"unsupported gene type {kind!r}")


def sample_chromosomes(chromosome_yaml: Path) -> list[dict]:
    doc = yaml.safe_load(chromosome_yaml.read_text(encoding="utf-8")) or {}
    content = (doc.get("chromosome") or {}).get("content")
    if not isinstance(content, dict):
        raise ValueError(f"{chromosome_yaml} has no chromosome.content mapping")
    base = {name: sample_gene(spec) for name, spec in content.items()}
    families = (content.get("model_family") or {}).get("values") or [None]
    samples = []
    for family in families:
        sample = dict(base)
        if family is not None:
            sample["model_family"] = family
        samples.append(sample)
    return samples


def check(chromosome_yaml: Path, fitness_py: Path) -> bool:
    """Return True when every sample chromosome scores finite and positive."""
    print(f"Local check: {chromosome_yaml.name} + {fitness_py.name}", flush=True)
    try:
        samples = sample_chromosomes(chromosome_yaml)
        module = load_fitness_module(fitness_py)
    except Exception as exc:  # noqa: BLE001 — report any setup error plainly
        print(f"  FAILED before scoring: {exc}", flush=True)
        return False

    ok = True
    with tempfile.TemporaryDirectory(prefix="earth_local_check_") as tmp:
        shutil.copy(TRAIN_CSV, Path(tmp) / TRAIN_CSV.name)
        shutil.copy(TEST_IDS_CSV, Path(tmp) / TEST_IDS_CSV.name)
        try:
            fitness = module.FitnessClass(tmp)
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED loading data in FitnessClass: {exc}", flush=True)
            return False
        for sample in samples:
            label = sample.get("model_family", "sample")
            try:
                result = fitness.calculate_fitness(sample)
                score = float(result.score)
            except Exception as exc:  # noqa: BLE001
                print(f"  {label}: FAILED: {exc}", flush=True)
                ok = False
                continue
            if (result.scalars or {}).get("error") or score <= ERROR_SCORE_CEILING:
                print(f"  {label}: FAILED: fitness returned its error score (see 'fitness error' above)", flush=True)
                ok = False
            elif not math.isfinite(score):
                print(f"  {label}: FAILED: score {score!r} is not finite", flush=True)
                ok = False
            else:
                print(f"  {label}: score={score:.4f}", flush=True)
    print("Local check OK." if ok else "Local check FAILED.", flush=True)
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--chromosome", type=Path, default=_REPO_ROOT / "earth" / "chromosome.yaml")
    parser.add_argument("--fitness", type=Path, default=_REPO_ROOT / "earth" / "fitness.py")
    args = parser.parse_args()
    return 0 if check(args.chromosome, args.fitness) else 1


if __name__ == "__main__":
    sys.exit(main())

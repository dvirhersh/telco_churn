"""Compare saved Earth runs side by side.

Usage (from repo root):
    python earth/compare_runs.py                 # every run under work/runs/
    python earth/compare_runs.py run1 run2       # just these runs

For each run: status, generations, champion hit@400 (mean, std, per fold), model
family and features. Then the lines of chromosome.yaml / fitness.py that differ
from the first run, so you can see the one thing you changed.
No Earth calls; reads work/runs/<name>/ only.
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_local import load_fitness_module  # noqa: E402

RUNS_DIR = _REPO_ROOT / "work" / "runs"


def load_run(run_dir: Path) -> dict | None:
    champ_path = run_dir / "champion_chromosome.json"
    if not champ_path.is_file():
        return None
    champion = json.loads(champ_path.read_text(encoding="utf-8"))
    genes = champion.get("chromosome") or {}
    genes = genes.get("content", genes)
    scalars = champion.get("scalars") or {}

    features = None
    fitness_py = run_dir / "fitness.py"
    if fitness_py.is_file() and "feature_mask" in genes:
        try:
            names = load_fitness_module(fitness_py).FEATURES
            features = [n for n, keep in zip(names, genes["feature_mask"]) if keep]
        except Exception:  # noqa: BLE001 — feature names are a nice-to-have
            features = None

    per_fold = scalars.get("hit_rate_at_400_per_fold") or {}
    return {
        "name": run_dir.name,
        "status": champion.get("status"),
        "generation": champion.get("generation"),
        "score": champion.get("fitness_score"),
        "std": scalars.get("hit_rate_at_400_std"),
        "per_fold": [per_fold[k] for k in sorted(per_fold)],
        "model_family": genes.get("model_family"),
        "features": features,
        "genes": genes,
    }


def fmt(value, digits: int = 4) -> str:
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return "-" if value is None else str(value)


def file_diff(first: Path, other: Path) -> list[str]:
    if not first.is_file() or not other.is_file():
        return []
    lines = difflib.unified_diff(
        first.read_text(encoding="utf-8").splitlines(),
        other.read_text(encoding="utf-8").splitlines(),
        fromfile=str(first.relative_to(_REPO_ROOT)),
        tofile=str(other.relative_to(_REPO_ROOT)),
        n=0,
        lineterm="",
    )
    return list(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("runs", nargs="*", help="Run names under work/runs/ (default: all)")
    args = parser.parse_args()

    names = args.runs or sorted(p.name for p in RUNS_DIR.glob("*") if p.is_dir())
    runs = []
    for name in names:
        run = load_run(RUNS_DIR / name)
        if run is None:
            print(f"{name}: no champion_chromosome.json yet (still running? try --collect)")
            continue
        runs.append(run)
    if not runs:
        print(f"No finished runs under {RUNS_DIR.relative_to(_REPO_ROOT)}.")
        return 1

    print(f"\n{'run':<10}{'status':<12}{'gen':>5}{'hit@400':>10}{'std':>8}  {'model':<22}per-fold")
    for run in runs:
        folds = " ".join(fmt(x, 3) for x in run["per_fold"])
        print(
            f"{run['name']:<10}{fmt(run['status']):<12}{fmt(run['generation']):>5}"
            f"{fmt(run['score']):>10}{fmt(run['std'], 3):>8}  {fmt(run['model_family']):<22}{folds}"
        )

    print("\nChampion features:")
    for run in runs:
        feats = run["features"]
        shown = f"{len(feats)}: {', '.join(feats)}" if feats is not None else "-"
        print(f"  {run['name']}: {shown}")

    first = RUNS_DIR / runs[0]["name"]
    for run in runs[1:]:
        other = RUNS_DIR / run["name"]
        for filename in ("chromosome.yaml", "fitness.py"):
            diff = file_diff(first / filename, other / filename)
            if diff:
                print(f"\nWhat {run['name']} changed in {filename} (vs {runs[0]['name']}):")
                print("\n".join(diff))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Upload train_clean.csv (+ test_ids.csv), launch the S4 Earth GA run, save the champion.

Run from repo root (requires .env):
    python earth/run_search.py

GA settings match the Earth UI run (ai1 block of earth/chromosome.yaml). The run
stops on Earth's own stagnation rules; there is no teaching-budget abort.
test_clean.csv carries labels and is never uploaded.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from earth_client import (  # noqa: E402
    BASE,
    CHURN_TEMPLATE_ID,
    auth,
    clone_template,
    launch,
    poll,
    upload_dataset,
)

TRAIN_CSV = _REPO_ROOT / "data" / "train_clean.csv"
TEST_IDS_CSV = _REPO_ROOT / "data" / "test_ids.csv"
CHROMOSOME = _REPO_ROOT / "earth" / "chromosome.yaml"
FITNESS_PY = _REPO_ROOT / "earth" / "fitness.py"
OUT_DIR = _REPO_ROOT / "work" / "optimization"
POLL_SECONDS = 30


def upload_extra_asset(session, headers, dataset_id: str, csv_path: Path) -> bool:
    """Add a second CSV asset to an existing dataset. Returns False on failure."""
    try:
        with open(csv_path, "rb") as f:
            resp = session.post(
                f"{BASE}/api/assets/{dataset_id}/upload",
                files={"file": (csv_path.name, f, "text/csv")},
                headers=headers,
                timeout=300,
            )
    except Exception as exc:  # noqa: BLE001 — optional asset; warn and continue
        print(f"WARNING: {csv_path.name} upload failed ({exc!r})", flush=True)
        return False
    if not resp.ok:
        print(
            f"WARNING: {csv_path.name} upload returned HTTP {resp.status_code} "
            f"body_prefix={resp.text[:200]!r}",
            flush=True,
        )
        return False
    print(f"Uploaded {csv_path.name} to dataset {dataset_id}", flush=True)
    return True


def main() -> int:
    for path in (TRAIN_CSV, TEST_IDS_CSV, CHROMOSOME, FITNESS_PY):
        if not path.is_file():
            print(f"Missing {path}", flush=True)
            return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Authenticating (password_only=True)...", flush=True)
    session, headers = auth(password_only=True)

    name = f"s4-telco-churn-{int(time.time())}"
    print(f"Uploading {TRAIN_CSV} as dataset '{name}'...", flush=True)
    dataset_id = upload_dataset(session, headers, str(TRAIN_CSV), name)

    print(f"Uploading {TEST_IDS_CSV} to the same dataset...", flush=True)
    test_ids_uploaded = upload_extra_asset(session, headers, dataset_id, TEST_IDS_CSV)
    if not test_ids_uploaded:
        print(
            "Continuing without test_ids.csv: fitness keeps the 10 customers "
            "shared with the test set.",
            flush=True,
        )

    print("Cloning template / creating project...", flush=True)
    project_id = clone_template(
        session, headers, CHURN_TEMPLATE_ID, dataset_id, name
    )

    print("Launching experiment...", flush=True)
    exp_id = launch(
        session,
        headers,
        project_id,
        dataset_id,
        chromo_path=str(CHROMOSOME),
        code_files=[str(FITNESS_PY)],
        pop=20,
        elite_pct=0.05,
        mutation_pct=0.15,
        minutes=None,
        maximize=True,
        max_stagnation_loops=5,
        max_drifts=3,
        steady_threshold=0.001,
        generation_start_steady=10,
        look_back=11,
        enable_genetic_drift=True,
    )

    ids = {
        "dataset_id": dataset_id,
        "project_id": project_id,
        "experiment_id": exp_id,
        "train_csv": str(TRAIN_CSV.relative_to(_REPO_ROOT)),
        "test_ids_uploaded": test_ids_uploaded,
        "chromosome": str(CHROMOSOME.relative_to(_REPO_ROOT)),
    }
    (OUT_DIR / "earth_ids.json").write_text(
        json.dumps(ids, indent=2), encoding="utf-8"
    )
    print(json.dumps(ids, indent=2), flush=True)

    while True:
        time.sleep(POLL_SECONDS)
        state = poll(session, headers, exp_id)
        status = state.get("status")
        print(
            f"  [{status}] gen={state.get('generation')} score={state.get('score')}",
            flush=True,
        )
        if status in ("COMPLETED", "STAGNATED", "ERROR", "ABORTED"):
            break

    final = poll(session, headers, exp_id)
    champion = {
        "experiment_id": exp_id,
        "status": final.get("status"),
        "generation": final.get("generation"),
        "fitness_score": final.get("score"),
        "scalars": final.get("scalars") or {},
        "chromosome": final.get("chromosome"),
    }
    champ_path = OUT_DIR / "champion_chromosome.json"
    champ_path.write_text(json.dumps(champion, indent=2), encoding="utf-8")
    print(f"Wrote {champ_path}", flush=True)

    if final.get("status") == "ERROR":
        print("Experiment ended in ERROR.", flush=True)
        return 1
    if final.get("chromosome") is None:
        print("No champion chromosome returned.", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

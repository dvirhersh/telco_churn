"""Recover an aborted or interrupted Earth experiment result into the task registry.

Use when the local poller (`run_pathway.py`) was interrupted before it could write
artifacts and update the registry.

Scope (narrowed for safety):
  - Recovers and registers exactly one Earth run; does not modify existing entries.
  - `--select` is only accepted when the recovered Earth experiment status is COMPLETED.
  - Writes `recovery_manifest.json` alongside `earth_run_manifest.json`.
  - If an entry for the same `earth_run_id` already exists: fails with a clear error
    unless `--overwrite` is explicitly passed.

Usage
-----
python earth/recover_run.py \\
  --exp-id  <earth_experiment_id> \\
  --proj-id <earth_project_id> \\
  --ds-id   <earth_dataset_id> \\
  --task    phase3_main_search \\
  --run-id  20260628-154357__seed42 \\
  [--select]      # only accepted if Earth status == COMPLETED
  [--overwrite]   # replace existing registry entry if present
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from earth.earth_client import auth, poll  # noqa: E402


# Registry lives inside the optimization task output tree
_TASKS_ROOT = _REPO_ROOT / "outputs" / "optimization" / "tasks"


# --------------------------------------------------------------------------- #
# Chromosome resolution (mirrors run_pathway._resolve_chromosome)
# --------------------------------------------------------------------------- #

def _resolve_chromosome(chromosome: dict) -> dict:
    return {
        "routing_strategy":            chromosome.get("routing_strategy"),
        "algorithm":                   chromosome.get("algorithm"),
        "k":                           chromosome.get("k"),
        "gmm_covariance":              chromosome.get("gmm_covariance"),
        "representation_family":       chromosome.get("representation_family"),
        "pca_enabled":                 chromosome.get("pca_enabled"),
        "pca_n_components":            chromosome.get("pca_n_components"),
        "weight_global":               chromosome.get("weight_global"),
        "weight_component_totals":     chromosome.get("weight_component_totals"),
        "weight_component_modalities": chromosome.get("weight_component_modalities"),
        "assignment_mode":             chromosome.get("assignment_mode"),
        "anomaly_distance_percentile": chromosome.get("anomaly_distance_percentile"),
    }


# --------------------------------------------------------------------------- #
# Registry helpers
# --------------------------------------------------------------------------- #

def _load_registry(registry_path: Path) -> dict:
    if registry_path.exists():
        with open(registry_path) as f:
            return yaml.safe_load(f) or {}
    return {}


def _save_registry(registry_path: Path, registry: dict) -> None:
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    with open(registry_path, "w") as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False)


def _find_existing_entry(registry: dict, earth_run_id: str) -> dict | None:
    for entry in registry.get("runs") or []:
        if entry.get("earth_run_id") == earth_run_id:
            return entry
    return None


# --------------------------------------------------------------------------- #
# Main recovery logic
# --------------------------------------------------------------------------- #

def recover(
    exp_id: str,
    proj_id: str,
    ds_id: str,
    task_name: str,
    run_id: str,
    select: bool,
    overwrite: bool,
) -> None:
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

    task_dir = _TASKS_ROOT / task_name
    run_dir = task_dir / "earth_runs" / run_id
    registry_path = task_dir / "task_registry.yaml"

    # ── Guard: registry entry collision ─────────────────────────────────────
    registry = _load_registry(registry_path)
    existing = _find_existing_entry(registry, run_id)
    if existing and not overwrite:
        print(
            f"ERROR: An entry for earth_run_id='{run_id}' already exists in\n"
            f"  {registry_path}\n\n"
            f"  status={existing.get('status')}  fitness={existing.get('fitness_score')}\n\n"
            "Pass --overwrite to replace it.",
            file=sys.stderr,
        )
        sys.exit(1)

    # ── Guard: run directory collision ──────────────────────────────────────
    if run_dir.exists() and not overwrite:
        print(
            f"ERROR: Run directory already exists:\n  {run_dir}\n\n"
            "Pass --overwrite to replace it.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"[recover_run] Authenticating with Earth...", flush=True)
    session, headers = auth()

    print(f"[recover_run] Fetching experiment {exp_id}...", flush=True)
    earth_state = poll(session, headers, exp_id)

    earth_status = earth_state.get("status") or "unknown"
    fitness_score = earth_state.get("score")
    chromosome = earth_state.get("chromosome") or {}
    generation = earth_state.get("generation")
    scalars = earth_state.get("scalars") or {}

    print(f"[recover_run] Earth status: {earth_status}  fitness: {fitness_score}  generation: {generation}")

    # ── Guard: --select only if COMPLETED ───────────────────────────────────
    if select and earth_status.upper() != "COMPLETED":
        print(
            f"ERROR: --select requires Earth experiment status == COMPLETED, "
            f"but got '{earth_status}'.\n"
            "Re-run without --select to register without selecting.",
            file=sys.stderr,
        )
        sys.exit(1)

    # ── Write artifacts ──────────────────────────────────────────────────────
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[recover_run] Writing artifacts to {run_dir}", flush=True)

    # winning_chromosome.json
    with open(run_dir / "winning_chromosome.json", "w") as f:
        json.dump(chromosome, f, indent=2)

    # chromosome_resolved.yaml (Step 4 handoff)
    chromosome_resolved = _resolve_chromosome(chromosome)
    with open(run_dir / "chromosome_resolved.yaml", "w") as f:
        yaml.dump(chromosome_resolved, f, default_flow_style=False, sort_keys=False)

    # earth_run_manifest.json
    earth_manifest = {
        "earth_run_id": run_id,
        "task_name": task_name,
        "task_signature": None,
        "manifest_path": None,
        "earth_experiment_id": exp_id,
        "earth_project_id": proj_id,
        "earth_dataset_id": ds_id,
        "status": earth_status,
        "fitness_score": float(fitness_score) if fitness_score is not None else None,
        "generations": generation,
        "scalars": scalars,
        "created_at_utc": now_utc,
        "recovery_note": "Written by recover_run.py — original poller was interrupted",
    }
    with open(run_dir / "earth_run_manifest.json", "w") as f:
        json.dump(earth_manifest, f, indent=2)

    # recovery_manifest.json — provenance of the recovery itself
    recovery_manifest = {
        "recovery_tool": "earth/recover_run.py",
        "recovery_timestamp_utc": now_utc,
        "earth_experiment_id": exp_id,
        "earth_project_id": proj_id,
        "earth_dataset_id": ds_id,
        "earth_status_at_recovery": earth_status,
        "run_id": run_id,
        "task_name": task_name,
        "selected_for_step4": select,
        "overwrite_used": overwrite,
    }
    with open(run_dir / "recovery_manifest.json", "w") as f:
        json.dump(recovery_manifest, f, indent=2)

    print("[recover_run] Artifacts written:", flush=True)
    for fname in ("winning_chromosome.json", "chromosome_resolved.yaml",
                  "earth_run_manifest.json", "recovery_manifest.json"):
        print(f"  {run_dir / fname}")

    # ── Update task registry ─────────────────────────────────────────────────
    if not registry:
        registry = {"task_name": task_name, "runs": []}
    if "runs" not in registry or registry["runs"] is None:
        registry["runs"] = []

    new_entry = {
        "earth_run_id": run_id,
        "task_signature": None,
        "seed": None,
        "status": earth_status,
        "fitness_score": float(fitness_score) if fitness_score is not None else None,
        "generations": generation,
        "earth_project_id": proj_id,
        "earth_experiment_id": exp_id,
        "earth_dataset_id": ds_id,
        "fitness_units_amount": None,
        "selected_for_step4": select,
        "manifest_snapshot_path": None,
        "created_at_utc": now_utc,
        "recovery_note": "registered by recover_run.py",
        "scalars": scalars,
    }

    if existing and overwrite:
        # Replace in-place
        idx = next(
            i for i, e in enumerate(registry["runs"])
            if e.get("earth_run_id") == run_id
        )
        registry["runs"][idx] = new_entry
        print(f"[recover_run] Overwriting existing registry entry for {run_id}", flush=True)
    else:
        registry["runs"].append(new_entry)
        print(f"[recover_run] Appended new registry entry for {run_id}", flush=True)

    _save_registry(registry_path, registry)
    print(f"[recover_run] Registry updated: {registry_path}", flush=True)

    # ── Optionally update best_run convenience copy ──────────────────────────
    if select:
        best_run_dir = task_dir / "best_run"
        best_run_dir.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(run_dir / "chromosome_resolved.yaml",
                     best_run_dir / "chromosome_resolved.yaml")
        print(f"[recover_run] Convenience copy written: {best_run_dir / 'chromosome_resolved.yaml'}")

        # Write task_selection.json
        selection = {
            "task_name": task_name,
            "selected_run_id": run_id,
            "selection_reason": "manually selected via recover_run.py --select",
            "handoff_artifact": f"earth_runs/{run_id}/chromosome_resolved.yaml",
            "selected_at_utc": now_utc,
        }
        with open(task_dir / "task_selection.json", "w") as f:
            json.dump(selection, f, indent=2)
        print(f"[recover_run] task_selection.json updated: {task_dir / 'task_selection.json'}")

    print(f"\n[recover_run] Done. Run '{run_id}' registered for task '{task_name}'.")
    if select:
        print(f"  selected_for_step4: true — ready for: moxo materialize --task {task_name}")
    else:
        print(
            f"  To select this run for Step 4, re-run with --select "
            f"(only works when Earth status == COMPLETED)."
        )


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover an aborted Earth experiment result into the task registry.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--exp-id",   required=True, help="Earth experiment ID")
    parser.add_argument("--proj-id",  required=True, help="Earth project ID")
    parser.add_argument("--ds-id",    required=True, help="Earth dataset ID")
    parser.add_argument("--task",     required=True, help="Optimization task name (e.g. phase3_main_search)")
    parser.add_argument("--run-id",   required=True, help="Earth run ID to register (e.g. 20260628-154357__seed42)")
    parser.add_argument(
        "--select",
        action="store_true",
        default=False,
        help="Set selected_for_step4=true. Only accepted when Earth status == COMPLETED.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Replace an existing registry entry and run directory if they already exist.",
    )

    args = parser.parse_args()

    recover(
        exp_id=args.exp_id,
        proj_id=args.proj_id,
        ds_id=args.ds_id,
        task_name=args.task,
        run_id=args.run_id,
        select=args.select,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()

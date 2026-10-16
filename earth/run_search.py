"""Workshop 1 Earth search: upload train.csv, launch, poll, save the champion.

Run from the repo root:
    python earth/run_search.py                      # new experiment
    python earth/run_search.py --resume <exp_id>    # keep polling an existing one

Uploads work/exploration/train.csv only (never holdout.csv), plus
work/modeling/fitness.py and work/modeling/chromosome.yaml.
Writes, under work/optimization/:
    earth_run.json   ids + settings, written right after launch
    champion.json    best chromosome, score and scalars, updated while polling
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from earth_client import (BASE, CHURN_TEMPLATE_ID, RateLimitError,  # noqa: E402
                          TokenExpiredError, TransientPollError, auth,
                          clone_template, launch, poll, upload_dataset)

TRAIN_CSV = ROOT / "work" / "exploration" / "train.csv"
FITNESS = ROOT / "work" / "modeling" / "fitness.py"
CHROMOSOME = ROOT / "work" / "modeling" / "chromosome.yaml"
OUT = ROOT / "work" / "optimization"
RUN_JSON, CHAMPION_JSON = OUT / "earth_run.json", OUT / "champion.json"
TERMINAL = {"COMPLETED", "STAGNATED", "ERROR", "FAILED", "ABORTED", "STOPPED"}


def now() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def start(args) -> str:
    assert TRAIN_CSV.name == "train.csv" and "holdout" not in TRAIN_CSV.name
    session, headers = auth(password_only=True)
    name = f"{args.name}-{datetime.datetime.now():%Y%m%d-%H%M}"
    dataset_id = upload_dataset(session, headers, str(TRAIN_CSV), name)
    project_id = clone_template(session, headers, CHURN_TEMPLATE_ID, dataset_id, name)
    exp_id = launch(session, headers, project_id, dataset_id,
                    chromo_path=str(CHROMOSOME), code_files=[str(FITNESS)],
                    pop=args.pop, units=args.units, minutes=args.minutes,
                    max_stagnation_loops=args.stagnation)
    run = {"name": name, "experiment_id": exp_id, "project_id": project_id,
           "dataset_id": dataset_id, "launched_at": now(),
           "ui": f"{BASE}/", "dataset_file": "work/exploration/train.csv",
           "settings": {"pop": args.pop, "units": args.units, "minutes": args.minutes,
                        "max_stagnation_loops": args.stagnation}}
    OUT.mkdir(parents=True, exist_ok=True)
    RUN_JSON.write_text(json.dumps(run, indent=2))
    print(f"Saved ids to {RUN_JSON.relative_to(ROOT)}")
    return exp_id


def watch(exp_id: str, interval: int) -> None:
    session, headers = auth(password_only=True)
    last_gen = None
    while True:
        try:
            state = poll(session, headers, exp_id)
        except TokenExpiredError:
            session, headers = auth(password_only=True)
            continue
        except (RateLimitError, TransientPollError) as exc:
            print(f"  poll retry: {exc}")
            time.sleep(interval)
            continue

        if state["generation"] != last_gen or state["status"] in TERMINAL:
            print(f"  {now()} [{state['status']}] gen={state['generation']} "
                  f"best F1={state['score']}", flush=True)
            last_gen = state["generation"]
        if state["chromosome"] is not None:
            CHAMPION_JSON.write_text(json.dumps(
                {"experiment_id": exp_id, "status": state["status"],
                 "generation": state["generation"], "fitness_f1_validation": state["score"],
                 "scalars": state["scalars"], "chromosome": state["chromosome"],
                 "saved_at": now()}, indent=2))
        if state["status"] in TERMINAL:
            break
        time.sleep(interval)

    print(f"\nFinal status: {state['status']}")
    if state["chromosome"] is None:
        print("No champion chromosome returned.")
    else:
        print(f"Champion (validation F1 {state['score']}) saved to "
              f"{CHAMPION_JSON.relative_to(ROOT)}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--resume", metavar="EXP_ID", help="poll an existing experiment instead of launching")
    p.add_argument("--name", default="telco-churn-w1")
    p.add_argument("--pop", type=int, default=30)
    p.add_argument("--units", type=int, default=4)
    p.add_argument("--minutes", type=int, default=30)
    p.add_argument("--stagnation", type=int, default=10)
    p.add_argument("--interval", type=int, default=60, help="seconds between polls")
    args = p.parse_args()

    exp_id = args.resume or start(args)
    watch(exp_id, args.interval)


if __name__ == "__main__":
    main()

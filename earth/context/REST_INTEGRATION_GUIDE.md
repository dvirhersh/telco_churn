# Earth REST Integration Guide

A self-contained guide for driving the **Earth GA platform** over its REST API from
a Claude (or any LLM) agent. Copy this file into your project, supply your own
**credentials + chromosome.yaml + fitness.py + dataset CSV**, and your agent can
configure and run experiments end to end.

> This guide is written for an agent to follow. It captures both the documented
> contract and the **undocumented gotchas that only surface when you actually run**
> (the tables marked ⚠️). Everything here was validated against
> `https://earth.evolution.inc`.

---

## 0. TL;DR — the whole loop

```
auth ──▶ upload dataset ──▶ clone template (for valid GA config) ──▶
PATCH project (your chromosome + fitness) ──▶ POST /api/experiments (FULL fitness_unit!) ──▶
poll best-chromosome ──▶ abort when converged ──▶ rebuild winner locally for inference
```

Five things that will bite you if you skip them (details below):

1. Auth uses the Keycloak **`id_token`**, not `access_token`.
2. Start experiments with a **fully-populated `fitness_unit`** (incl. `compute_profile_id`) — the naive call 503s.
3. **Enum** chromosome genes must use `crossover: {type: error}`.
4. The `requirements` field is **accepted but not pip-installed** — only use pre-baked libs, or vendor pure-Python code.
5. The fitness `score` must be **strictly positive and finite** or GA selection breaks.

---

## 1. Prerequisites

```bash
pip install requests pyyaml pandas scikit-learn xgboost
# catboost is pre-installed on Earth workers; install locally only if your fitness imports it
```

Put your credentials in a `.env` file (never hard-code them):

```
EARTH_USER=you@yourcompany.com
EARTH_PASS=your-password
```

You provide four things per project:

| Input | What it is |
|---|---|
| `chromosome.yaml` | the GA search space (see §4) |
| `fitness.py` | a single file exposing `FitnessClass` (see §3) |
| `data.csv` | your training data (the production/scoring set stays local) |
| `.env` | your Earth credentials |

---

## 2. Key constants (Basic compute profile)

```
BASE                 = https://earth.evolution.inc
TOKEN_URL            = {BASE}/realms/earth/protocol/openid-connect/token
CHURN_TEMPLATE_ID    = fb775bea36244a829cd79f5d7364016b      # any valid template works
BASIC_COMPUTE_PROFILE= 6052020896a64dfab30ca96f9beca711      # ≤8 fitness units
```

Your account/templates/profiles may differ — list them with
`GET /api/templates` and `GET /api/compute-profiles` (or copy a `fitness_unit`
from any recently-RUNNING experiment via `GET /api/experiments/{id}`).

---

## 3. The fitness contract (what Earth runs)

Earth executes **one `fitness.py`** per worker. It must define:

```python
from pydantic import BaseModel
from typing import Union

class FitnessCalculationResult(BaseModel):
    score: float
    scalars: dict[str, Union[float, int]] | None = None   # FLAT, numeric only
    rows: dict[str, list] | None = None                   # short lists (≤10 items)

class FitnessClass:
    def __init__(self, dataset_root: str):
        # Called ONCE per worker. Load + split your data here.
        # ⚠️ GLOB the CSV — do NOT hardcode the filename (Earth may rename it):
        import glob, os, pandas as pd
        csv = sorted(glob.glob(os.path.join(dataset_root, "*.csv")))[0]
        self.data = pd.read_csv(csv)
        # ... preprocess, train/val split, stash on self ...

    def calculate_fitness(self, chromosome) -> FitnessCalculationResult:
        node = chromosome.get("content", chromosome)   # support both shapes
        # ... decode genes, train model(s), compute metric ...
        score = max(float(metric_value), 1e-9)          # ⚠️ strictly positive & finite
        return FitnessCalculationResult(score=score, scalars={...}, rows={...})
```

### Hard rules for `fitness.py`

| Rule | Why |
|---|---|
| **Glob the dataset filename**, never hardcode it | Earth may store it under a different name |
| **`score` strictly positive & finite** (`max(s, 1e-9)`, no NaN/Inf) | GA uses score as selection weight; ≤0 or NaN crashes selection |
| **No function calls inside `FitnessCalculationResult(...)`** | Hoist every value to a variable first; pass only variable names |
| **`scalars` flat & numeric**; put strings/labels in `rows` | Dashboard + serialization require numeric scalars |
| **`rows` = short lists** (≤10 items, primitives only) | UI/serialization limit |
| **Score on CV or a validation split, not the test set** | Otherwise GA overfits the specific test split |
| **Self-contained single file** | Earth runs one `fitness.py`; flatten any multi-module package |
| **Only pre-installed libraries** | `numpy/pandas/scikit-learn/xgboost/catboost` are available; `imbalanced-learn` is **not** |

---

## 4. The chromosome (the GA search space)

YAML with a top-level `chromosome:` of `type: dict`, whose `content:` holds your
genes. Supported gene types: `int`, `float`, `bool`, `enum`, `array`, nested `dict`.

### ⚠️ EVL gotchas that cause `400 "Chromosome is invalid"`

| Gene type | Required form |
|---|---|
| **enum** | needs `type`, `values` (≥2, unique), `generation: {type: uniform}`, and **`crossover: {type: error}`** (mutation-only — `random` is rejected) |
| **bool** | bare `{type: bool}` only — no generation/mutation/crossover blocks allowed |
| **int / float** | `generation`, `mutation` (with `step_size`/`percentage_change`), `crossover: {type: random}` or `range_uniform` |
| **array** (feature mask) | `min_size == max_size` when using `per_item`; `item_definition: {type: bool}` |
| **nested dict** (per-model hyperparams) | `type: dict` + `generation/mutation/crossover` + nested `content:` |

Minimal valid examples:

```yaml
chromosome:
  type: dict
  generation: { type: per_item, non_required_probability: 0 }
  mutation:   { percentage_to_mutate: 0.05 }
  crossover:  { type: per_item_crossover }
  content:

    # int gene
    threshold_steps:
      type: int
      min_value: 1
      max_value: 9
      generation: { type: uniform }
      mutation:   { step_size: 1, percentage_change: 0.2, max_magnitude: 0 }
      crossover:  { type: random }

    # float gene
    learning_rate:
      type: float
      min_value: 0.01
      max_value: 0.3
      generation: { type: uniform }
      mutation:   { percentage_change: 0.2 }
      crossover:  { type: range_uniform }

    # bool gene — bare type only
    use_scaling:
      type: bool

    # enum gene — crossover MUST be 'error'
    scaling_method:
      type: enum
      values: [none, standard, robust]
      generation: { type: uniform }
      mutation:   { type: random }
      crossover:  { type: error }      # ⚠️ required for enums

    # array / feature mask
    feature_selection:
      type: array
      generation: { type: per_item }
      mutation:   { type: random, percentage_to_mutate: 0.1 }
      crossover:  { type: single_point, per_item_select_strategy: random }
      min_size: 30
      max_size: 30          # min==max for per_item arrays
      item_definition: { type: bool }

    # nested per-model hyperparameter dict
    xgboost:
      type: dict
      generation: { type: per_item, non_required_probability: 0.1 }
      mutation:   { type: random, percentage_to_mutate: 0.3 }
      crossover:  { type: per_item_crossover }
      content:
        n_estimators:
          type: int
          min_value: 100
          max_value: 500
          generation: { type: uniform }
          mutation:   { step_size: 20, percentage_change: 0.2 }
          crossover:  { type: random }
```

> **Validate locally before launching:** `python -c "import yaml; yaml.safe_load(open('chromosome.yaml'))"`.
> A YAML that parses can still be rejected by Earth's EVL schema — the table above
> covers the rejections we actually hit.

### Match metric orientation

Set `is_maximum_problem` (in the GA config) to your metric:
- maximize → F1, Accuracy, ROC-AUC, R², Silhouette, **profit**
- minimize → RMSE, MAE, Davies-Bouldin

---

## 5. The REST workflow (copy-paste helper)

Save this as `earth_client.py`. It wraps the entire loop including the **L11 fix**
(full `fitness_unit`). Your agent calls `launch(...)` then `poll(...)`.

```python
"""Minimal Earth REST client — auth, upload, clone, patch, launch, poll, abort."""
import os, sys, time, yaml, requests
from pathlib import Path

BASE = "https://earth.evolution.inc"
BASIC_PROFILE = {
    "compute_profile_id": "6052020896a64dfab30ca96f9beca711",
    "compute_profile_name": "Basic",
    "compute_profile_launcher_cpus": 1, "compute_profile_launcher_memory": "2Gi",
    "compute_profile_worker_cpus": 1,   "compute_profile_worker_memory": "8Gi",
    "fitness_cpu": 2, "fitness_memory": 1.0,
}

def _env(k):
    v = os.environ.get(k)
    if v: return v
    for line in Path(".env").read_text().splitlines():
        if line.strip().startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"Missing {k} (set env var or .env)")

def auth():
    s = requests.Session()
    r = s.post(f"{BASE}/realms/earth/protocol/openid-connect/token", data={
        "grant_type": "password", "client_id": "user-auth",
        "username": _env("EARTH_USER"), "password": _env("EARTH_PASS"), "scope": "openid"})
    r.raise_for_status(); t = r.json()
    # ⚠️ Earth accepts the id_token, not access_token
    return s, {"Authorization": f"Bearer {t.get('id_token') or t['access_token']}"}

def upload_dataset(s, H, csv_path, name):
    ds = s.post(f"{BASE}/api/datasets", json={"name": name, "shared": False}, headers=H).json()
    with open(csv_path, "rb") as f:
        s.post(f"{BASE}/api/assets/{ds['id']}/upload",
               files={"file": (Path(csv_path).name, f, "text/csv")}, headers=H)
    return ds["id"]

def clone_template(s, H, template_id, dataset_id, title):
    t = s.get(f"{BASE}/api/templates/{template_id}", headers=H).json()
    body = {"title": title, "shared": False,
            "chromosome": t.get("chromosome"), "fitness": t.get("fitness"),
            "configuration": t.get("configuration"), "dataset_id": dataset_id}
    return s.post(f"{BASE}/api/projects", json=body, headers=H).json()["id"]

def ga_config(pop, minutes, maximize):
    return {
      "ai1": {
        "ga": {"population_size": pop, "elite_percentage": 0.1,
               "mutation_percentage": 0.6, "unique_mutation_percentage": 0,
               "recalculate_elite_fitness": False},
        "flow_control": {"minimum_problem_sufficient_fitness": 0.01,
               "max_stagnation_loops": 15, "max_drifts_with_no_change": 8,
               "steady_threshold": 0.001, "generation_to_start_check_steady_state": 30,
               "how_many_generations_look_back": 8,
               "how_many_generations_look_back_for_local_optimization": -1,
               "max_constant_loops": -1, "time_limit": int(minutes*60)},
        "cumulative_genetic_drift": {"chosen_drifts_names":
               ["genesis_crossover_drift","genesis_genetic_drift","mutation_genetic_drift"]},
        "genesis_genetic_drift": {"drift_fraction": 0.2},
        "mutation_genetic_drift": {"drift_fraction": 0.2, "drift_factor": 2},
        "genesis_crossover_drift": {"drift_fraction": 0.2},
        "mutation_pool": {"type": "DefaultMutationPoolCreator"},
        "crossover_pool": {"type": "DefaultCrossoverPoolCreator",
                           "min_fitness_value": 0, "max_fitness_value": 1},
        "is_maximum_problem": bool(maximize), "generate_final_mutations": False},
      "ai2": {"output": {"concurrency": 32, "cpu_cores": 1}}}

def launch(s, H, project_id, dataset_id, chromo_path, fitness_path,
           pop=25, units=8, minutes=20, maximize=True):
    chrom_yaml   = open(chromo_path).read()
    fitness_code = open(fitness_path).read()
    # 1) PATCH project with your chromosome + fitness + GA config
    patch = {"chromosome": {"value": chrom_yaml},
             "fitness": {"code": [{"key": "fitness.py", "value": fitness_code,
                                   "is_folder": False}], "requirements": []},
             "configuration": ga_config(pop, minutes, maximize),
             "dataset_id": dataset_id}
    r = s.patch(f"{BASE}/api/projects/{project_id}", json=patch, headers=H)
    r.raise_for_status()
    # 2) Re-GET so the chromosome YAML is parsed back to a dict
    proj = s.get(f"{BASE}/api/projects/{project_id}", headers=H).json()
    chrom = yaml.safe_load(proj["chromosome"]["value"])
    chrom = chrom.get("chromosome", chrom)
    cfg = proj.get("configuration") or {}
    cfg.setdefault("ai1", {}).setdefault("ga", {})
    cfg["ai1"]["ga"]["run_on_cloud"] = True
    cfg["ai1"]["ga"]["calculate_fitness_as_batch"] = True
    code_files = [{"key": f["key"], "is_folder": False, "value": f["value"]}
                  for f in (proj.get("fitness") or {}).get("code", [])]
    # 3) ⚠️ L11: send a FULLY-POPULATED fitness_unit incl. compute_profile_id
    fu = dict(BASIC_PROFILE)
    fu["fitness_units_amount"] = units
    fu["total_cpus"]   = units * fu["fitness_cpu"] + 1
    fu["total_memory"] = f"{(units + 1) * 8 + 2}.00Gi"
    body = {"name": proj.get("title", "Experiment"), "project_id": project_id,
            "shared": False,
            "configuration": {"chromosome": chrom, "lom_configuration": cfg,
                              "dataset_id": dataset_id, "code_files": code_files,
                              "fitness_unit": fu, "experiment_type": "REGULAR"}}
    r = s.post(f"{BASE}/api/experiments", json=body, headers=H)
    if not r.ok:
        # On 503, check quota then fall back to fewer units
        print("launch error:", r.status_code, r.text[:300])
        print("running-count:", s.get(f"{BASE}/api/experiments/running-count", headers=H).text)
        r.raise_for_status()
    return r.json()["id"]

def poll(s, H, exp_id):
    exp = s.get(f"{BASE}/api/experiments/{exp_id}", headers=H).json()
    out = {"status": exp.get("status"), "generation": exp.get("generations_passed")}
    try:
        best = s.get(f"{BASE}/api/experiments/{exp_id}/best-chromosome", headers=H).json()
        ind = best["individual"]
        out["score"] = ind.get("fitness_score")
        out["scalars"] = ind.get("fitness_composition", {}).get("scalars", {})
        out["chromosome"] = ind.get("chromosome")
    except Exception:
        pass
    return out

def abort(s, H, exp_id):
    s.post(f"{BASE}/api/experiments/{exp_id}/abort", headers=H)
```

---

## 6. Agent runbook (the order to do things)

```python
import json, time
from earth_client import (auth, upload_dataset, clone_template, launch, poll, abort)

s, H = auth()

# 1. Upload your training data
dataset_id = upload_dataset(s, H, "data/my_train.csv", "My Churn Train")

# 2. Clone any template to inherit a valid GA configuration
project_id = clone_template(s, H,
    "fb775bea36244a829cd79f5d7364016b", dataset_id, "My Churn Project")

# 3. Launch with your chromosome + fitness
exp_id = launch(s, H, project_id, dataset_id,
    "my_chromosome.yaml", "my_fitness.py",
    pop=25, units=8, minutes=20, maximize=True)
print("experiment:", exp_id)

# 4. Poll until converged (agent decides cadence; ~2-4 min between checks)
prev = None
while True:
    time.sleep(180)
    st = poll(s, H, exp_id)
    print(st["status"], "gen", st.get("generation"), "score", st.get("score"))
    if st["status"] in ("COMPLETED", "STAGNATED", "ERROR"):
        break
    # early-exit when score is stable for two checks
    if prev is not None and st.get("score") and abs(st["score"] - prev) < 0.01:
        abort(s, H, exp_id); break
    prev = st.get("score")

# 5. Save the winning chromosome and rebuild it locally for inference
best = poll(s, H, exp_id)
open("winning_chromosome.json", "w").write(json.dumps(best["chromosome"], indent=2))
```

**Pre-flight (always do these before `launch`):**
1. `yaml.safe_load(open("chromosome.yaml"))` parses.
2. Stub-test `fitness.py`: instantiate `FitnessClass("data_dir")`, call
   `calculate_fitness(sample_chromosome)`, assert `score` is a positive finite float
   and every `scalars` value is numeric. This catches runtime bugs the validator misses.

---

## 7. ⚠️ Gotchas reference (learned by running, not in the docs)

| Symptom | Cause | Fix |
|---|---|---|
| `401 Unauthorized` | used `access_token` | use the Keycloak **`id_token`** |
| `503 "service unavailable"` on experiment start | `fitness_unit` missing `compute_profile_id` | send the **full** `fitness_unit` (see `launch`); it's almost never a real outage |
| `400 "Chromosome is invalid"` | enum gene used `crossover: random` | enums require **`crossover: {type: error}`** |
| `400` on a `bool` gene | added generation/mutation/crossover to it | bool genes are **bare** `{type: bool}` only |
| Worker `ModuleNotFoundError` | imported a non-bundled lib (e.g. `imblearn`) | the `requirements` field is **accepted but not installed**; use bundled libs or vendor pure-Python code |
| GA crashes / weird selection | `score` ≤ 0 or NaN/Inf | clamp `score = max(s, 1e-9)`, sanitize NaN/Inf to 0 |
| Earth "wins" look too good | scored fitness on the test set | score on **CV/validation**; evaluate test once at the end |
| Empty GA config / silent launch fail | created project without `ai1`/`ai2` | **clone a template** (carries valid GA config) or PATCH `configuration` explicitly |
| `find` the right `fitness_unit` | unsure of profile fields | copy `configuration.fitness_unit` from any recently-RUNNING experiment: `GET /api/experiments/{id}` |

---

## 8. Endpoint cheat-sheet

| Action | Method + path |
|---|---|
| Get token | `POST /realms/earth/protocol/openid-connect/token` |
| Create dataset | `POST /api/datasets` |
| Upload file to dataset | `POST /api/assets/{dataset_id}/upload` (multipart `file`) |
| List / get template | `GET /api/templates` · `GET /api/templates/{id}` |
| Create project | `POST /api/projects` |
| Update project (push chromosome/fitness) | `PATCH /api/projects/{id}` |
| Get project | `GET /api/projects/{id}` |
| Start experiment | `POST /api/experiments` (full `fitness_unit`!) |
| Experiment status | `GET /api/experiments/{id}` |
| Best chromosome so far | `GET /api/experiments/{id}/best-chromosome` |
| Abort experiment | `POST /api/experiments/{id}/abort` |
| Concurrency quota | `GET /api/experiments/running-count` |

---

## 9. Tuning knobs

| Knob | Where | Effect |
|---|---|---|
| `population_size` (`--pop`) | GA config | bigger = broader search, slower generations |
| `fitness_units_amount` (`--units`) | `fitness_unit` | parallel workers (≤8 on Basic) |
| `time_limit` (`--minutes`) | GA config | wall-clock budget |
| `is_maximum_problem` | GA config | match to metric orientation (§4) |
| CV folds in `fitness.py` | your code | fewer folds = faster evals |

Smaller population + max units + a lean dataset = fast generations and a visible
climb — ideal for a first run. Scale up once the pipeline is proven.

---

*Provide your own credentials, chromosome, fitness, and data — everything else in
this guide is reusable as-is.*

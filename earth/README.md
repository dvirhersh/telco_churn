# Earth integration (this repository)

Reusable Earth REST client and contracts for Workshop 1.

## Workshop use

```bash
python earth/check_connection.py                     # login check, no experiment
python earth/check_local.py                          # local pre-flight of chromosome + fitness
python earth/run_search.py --name run1               # upload, launch, poll, save to work/runs/run1/
python earth/compare_runs.py run1 run2               # champions side by side
python earth/validate_chromosome.py earth/chromosome.yaml   # Earth's own schema check
```

`run_search.py` uploads `data/train_clean.csv` plus `data/test_ids.csv` (so the
fitness drops the 10 customers shared with the test set). `data/test_clean.csv`
carries labels and is never uploaded. Options: `--chromosome`, `--fitness`,
`--pop` (10), `--units` (5), `--cpus` (1), `--minutes` (15), `--no-wait`,
`--collect`. Other GA settings come from the YAML's `ai1` block.

```python
from earth_client import auth, upload_dataset, clone_template, launch, poll, abort

session, headers = auth(password_only=True)
```

## Important files

| File | Role |
|------|------|
| `chromosome.yaml` | Search space + GA settings (Earth UI export) |
| `fitness.py` | `FitnessClass`: 5-fold CV hit rate among the top 400 calls |
| `run_search.py` | Local check, upload, launch, poll, save one run |
| `check_local.py` | Runs the fitness locally on sample chromosomes |
| `compare_runs.py` | Compares saved runs and shows what changed |
| `WALKTHROUGH.md` | Reading guide for the chromosome and fitness |
| `earth_client.py` | Auth, dataset upload, launch, poll, abort |
| `check_connection.py` | Password-only auth + template + running-count |
| `validate_chromosome.py` | `POST /api/evl/chromosome/validate` + negative control |
| `context/` | Earth GA contracts (see `NOTES_FOR_THIS_REPO.md`) |

## Auth

Set `EARTH_USER` / `EARTH_PASS` in `.env` (login name often without `@domain`).
Workshop scripts call `auth(password_only=True)` so a bad password exits instead
of hanging on device code. Auth prefers the ZITADEL **access_token** (it carries
`org_id` for `x-jwt-org-id`). Optional: set `EARTH_ORG_ID` explicitly. Tokens are
cached in `.earth_token_cache.json` (gitignored).

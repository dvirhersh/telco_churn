# Earth integration (this repository)

Reusable Earth REST client and contracts for Workshop 1.

## Workshop use

```bash
# Student readiness (no experiment)
python earth/check_connection.py

# Chromosome schema check
python earth/validate_chromosome.py earth/chromosome.yaml

# Upload data and run the same search as the Earth UI
python earth/run_search.py
```

`run_search.py` uploads `data/train_clean.csv` plus `data/test_ids.csv` (so the
fitness drops the 10 customers shared with the test set), clones the template
project, launches `chromosome.yaml` + `fitness.py` with the GA settings of the UI
run, and writes `work/optimization/earth_ids.json` and `champion_chromosome.json`.
`data/test_clean.csv` carries labels and is never uploaded.

```python
from earth_client import auth, upload_dataset, clone_template, launch, poll, abort

session, headers = auth(password_only=True)
```

## Important files

| File | Role |
|------|------|
| `earth_client.py` | Auth, dataset upload, launch, poll, abort |
| `run_search.py` | Upload, launch, poll, save champion |
| `chromosome.yaml` | Search space + GA settings (Earth UI export) |
| `fitness.py` | `FitnessClass`: 5-fold CV hit rate among the top 400 calls |
| `check_connection.py` | Password-only auth + template + running-count |
| `validate_chromosome.py` | `POST /api/evl/chromosome/validate` + negative control |
| `context/` | Earth GA contracts (see `NOTES_FOR_THIS_REPO.md`) |

## Auth

Set `EARTH_USER` / `EARTH_PASS` in `.env` (login name often without `@domain`).
Workshop scripts call `auth(password_only=True)` so a bad password exits instead
of hanging on device code. Auth prefers the ZITADEL **access_token** (it carries
`org_id` for `x-jwt-org-id`). Optional: set `EARTH_ORG_ID` explicitly. Tokens are
cached in `.earth_token_cache.json` (gitignored).

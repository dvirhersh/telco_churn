# Earth integration (this repository)

Reusable Earth REST client and contracts for Workshop 1.

## Workshop use

```bash
# Student readiness (no experiment)
python earth/check_connection.py

# Chromosome schema check (after you write work/modeling/chromosome.yaml)
python earth/validate_chromosome.py work/modeling/chromosome.yaml
```

On the facilitator solution pathway, `earth/run_search.py` uploads
`work/exploration/train.csv` and the sibling modules under `work/modeling/`.

```python
from earth_client import auth, upload_dataset, clone_template, launch, poll, abort

session, headers = auth(password_only=True)
```

## Important files

| File | Role |
|------|------|
| `earth_client.py` | Auth, dataset upload, launch, poll, abort |
| `check_connection.py` | Password-only auth + template + running-count |
| `validate_chromosome.py` | `POST /api/evl/chromosome/validate` + negative control |
| `context/` | Earth GA contracts (inherited; see `NOTES_FOR_THIS_REPO.md`) |
| `reference/moxo_era_spike_findings.md` | Dated platform observations |

## Auth

Set `EARTH_USER` / `EARTH_PASS` in `.env` (login name often without `@domain`).
Workshop scripts call `auth(password_only=True)` so a bad password exits instead
of hanging on device code. Auth prefers the ZITADEL **access_token** (it carries
`org_id` for `x-jwt-org-id`). Optional: set `EARTH_ORG_ID` explicitly. Tokens are
cached in `.earth_token_cache.json` (gitignored).

## Reference only (do not run as the workshop)

`chromosome.yaml` and `recover_run.py` are inherited MOXO clustering history.
They are not the Workshop 1 search space. The workshop chromosome lives under
`work/modeling/` after formulation.

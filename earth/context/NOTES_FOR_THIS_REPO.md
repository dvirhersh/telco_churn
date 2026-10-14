# Notes for this repository

The documents under `earth/context/` are general Earth contract references. They
predate this project; read them with these caveats.

1. **Sibling modules work.** `earth_client.launch(code_files=[...])` uploads
   several sibling `.py` files, and they import each other on the workers. This
   repo ships a single `earth/fitness.py`.

2. **UI-exported chromosome YAML.** `earth/chromosome.yaml` is the export from the
   Earth UI: `fitness_function`, `chromosome`, and the GA settings in `ai1` / `ai2`.
   `earth/run_search.py` takes the GA settings from `ai1`, except population, time
   cap, and compute (`--pop`, `--minutes`, `--units`, `--cpus`), which are smaller
   for class. So an API class run does not match the UI run exactly.

3. **AVAILABLE_PACKAGES.md is an undated snapshot.** Treat it as "packages known
   to be on workers when this folder was copied," not a live inventory.
   pandas, NumPy, SciPy, scikit-learn, xgboost, and pydantic are listed and used
   by `earth/fitness.py`; `requirements.txt` pins the same versions locally.

4. **Auth.** `earth/earth_client.py` logs in with `POST /api/auth/login`
   (`{username, password}`, login name often without `@domain`) and uses the
   returned **access_token**, which carries the `org_id` sent as `x-jwt-org-id`.
   The old Keycloak `/realms/earth/...` token endpoint no longer works.

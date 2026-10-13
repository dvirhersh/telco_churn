# Notes for this repository

The documents under `earth/context/` are general Earth contract references. They
predate this project; read them with these caveats.

1. **Sibling modules work.** `REST_INTEGRATION_GUIDE.md` says fitness should be a
   "self-contained single file." `earth_client.launch(code_files=[...])` uploads
   several sibling `.py` files, and they import each other on the workers. This
   repo ships a single `earth/fitness.py`.

2. **UI-exported chromosome YAML.** `earth/chromosome.yaml` is the export from the
   Earth UI: `fitness_function`, `chromosome`, and the GA settings in `ai1` / `ai2`.
   `earth/run_search.py` passes the same GA settings to `launch()`, so an API run
   matches the UI run.

3. **AVAILABLE_PACKAGES.md is an undated snapshot.** Treat it as "packages known
   to be on workers when this folder was copied," not a live inventory.
   pandas, NumPy, scikit-learn, xgboost, and pydantic are listed and used by
   `earth/fitness.py`.

4. **Auth.** Keycloak `/realms/earth/protocol/openid-connect/token` now serves the
   SPA HTML. Use `POST /api/auth/login` with `{username, password}` (login name
   often without `@domain`). OIDC discovery is at
   `/.well-known/openid-configuration` (ZITADEL). Device-code is listed but not
   enabled for the web client.

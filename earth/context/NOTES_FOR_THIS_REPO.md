# Notes for this repository

These documents under `earth/context/` were inherited from the MOXO clustering
project along with the rest of the `earth/` folder. They are the best available
Earth contract reference and are kept as inherited text.

Corrections / caveats for this repo:

1. **Sibling modules work.** `REST_INTEGRATION_GUIDE.md` says fitness should be a
   "self-contained single file." That advice is contradicted by the working
   `earth_client.launch()` path, which uploads multiple sibling `.py` files
   (MOXO shipped `fitness.py` + `moxo_config.py`). This demo uploads
   `fitness.py` + `renderer.py`.

2. **Clustering gene catalogue is an instance, not a constraint.**
   `GA_ASSUMPTIONS.md` ends with MOXO-specific genes (routing, k, PCA, …).
   Those are not required by Earth; any valid chromosome schema is fine.

3. **AVAILABLE_PACKAGES.md is an undated snapshot.** Treat it as "packages known
   to be on workers when this folder was copied," not a live inventory.
   Pillow, OpenCV headless, NumPy, SciPy, and matplotlib are listed and used
   by this demo.

4. **Do not import MOXO runtime from the demo.** `earth/fitness.py`,
   `earth/run_pathway.py`, `earth/moxo_config.py`, and related files are
   MOXO-specific reference / dead weight until a later cleanup pass.
   The image demo uses `earth/earth_client.py` and `earth/validate_chromosome.py`
   only.

5. **Auth changed (post-MOXO copy).** Keycloak
   `/realms/earth/protocol/openid-connect/token` now serves the SPA HTML.
   Use `POST /api/auth/login` with `{username, password}` (login name often
   without `@domain`). OIDC discovery is at `/.well-known/openid-configuration`
   (ZITADEL). Device-code is listed but not enabled for the web client.

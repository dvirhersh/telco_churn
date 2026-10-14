# Workshop state management

Humans and coding agents use this file to decide **where a change belongs**.

## Branches and tags

| Branch / tag | What it is |
|--------------|------------|
| `s4` | The S4 live session (from the Earth UI to the API). Complete on purpose: the chromosome and fitness from the UI run are included so students can run them as is. No tags yet. |
| `main`, `workshop-1-start-vN` | Workshop 1 student starter (IBM five-table data, F1). Not used in S4. |
| `facilitator/solution`, `workshop-1-solution-vN` | Workshop 1 verified pathway. Facilitator-only. |

Do not merge `s4` into `main` or `facilitator/solution`.

## Changes on `s4`

- Session material (README, `AGENT_PROMPTS.md`, `earth/`, `data/`, `context/`)
  is committed on `s4`.
- Student runs live under `work/runs/<name>/` on each student's machine. They
  are outputs, not session material; do not commit them to `s4`.
- Homework material (extended dataset, framing, baseline flow) will get its own
  branch or folder; keep it out of the live-session steps.

## Agent checklist

- [ ] The change is on the right branch (`s4` for the live session).
- [ ] `earth/chromosome.yaml` and `earth/fitness.py` still pass
      `python earth/check_local.py`.
- [ ] `data/test_clean.csv` is never uploaded or read by search code.
- [ ] `.env` and `.earth_token_cache.json` are never committed.

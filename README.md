# Earth DS Workshop — Churn Prediction (S4: from the Earth UI to the API)

## What you will build

The same churn search you ran in the Earth UI, now driven from code through the
Earth API: upload the data, launch the search, read the champion, check it, and
score it once on the locked test set.

The decision: each month the retention team calls the **400 customers most likely
to leave**. The metric is **hit@400**, the share of those 400 who actually churn.

## What you will learn

- How to drive an Earth search end to end through the REST API
- How to check that an API run matches a UI run (same chromosome, fitness, GA settings)
- How to read a champion critically: search optimism, fresh split seeds, one test read
- How to partner with a coding agent without giving up the DS decisions

Project framing: [context/project_context.md](context/project_context.md).
Pathway and rules: [context/workshop_pathway.md](context/workshop_pathway.md).

## Repository structure

```text
data/                   train_clean.csv, test_clean.csv, test_ids.csv, data_dictionary.md
earth/                  Earth REST client, chromosome.yaml + fitness.py (from the UI run),
                        run_search.py, connection and chromosome checks
context/                Project context, pathway, state management, DS practices
context/template_churn/ Reference chromosome/fitness examples (not runtime)
work/                   Your work (empty at start except framing.md)
```

## Data

The data was cleaned and split in S1/S2. Do not re-split it.

| File | Rows | Role |
|------|------|------|
| `data/train_clean.csv` | 5,638 | Everything before the final check: search, baselines, re-checks |
| `data/test_ids.csv` | 1,415 | Customer IDs only; uploaded with train so the fitness drops the 10 customers shared with test |
| `data/test_clean.csv` | 1,415 | Locked test set with labels; scored **once**, at the end; never uploaded to Earth |

Column meanings: [data/data_dictionary.md](data/data_dictionary.md).

## Prerequisites

- Python 3.12
- An Earth account (`EARTH_USER` / `EARTH_PASS`)

## Pathway

Work under `work/`. Ask your coding agent to implement each step after you make
the DS decisions. Read the code, run it, then continue.

### 1. Set up

```bash
git checkout s4
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set EARTH_USER / EARTH_PASS
python earth/check_connection.py
```

`python --version` should print Python 3.12.x after activate. If `python3.12` is
not on your `PATH`, create the environment with a Python 3.12 interpreter you
already have (for example `~/.pyenv/versions/3.12.3/bin/python -m venv .venv`).
On Windows, activate with `.venv\Scripts\activate`.

Expected from `check_connection.py`: authentication succeeds, the template GET
returns 200, and `running-count` prints. No dataset or experiment is created.

### 2. Look at the data

Open `data/train_clean.csv` with [data/data_dictionary.md](data/data_dictionary.md)
beside it. Check shape, churn rate (about 26.5%), and the 19 feature columns the
fitness uses. Fill [work/framing.md](work/framing.md).

### 3. Read the chromosome and fitness from the UI run

`earth/chromosome.yaml` and `earth/fitness.py` are the files you ran in the Earth
UI. Read them before running anything: which genes Earth may change, which
features the mask covers, how hit@400 is computed (5 stratified folds, seed 42,
top 80 per validation fold), and the GA settings in the `ai1` block.

### 4. Validate the chromosome

```bash
python earth/validate_chromosome.py earth/chromosome.yaml
```

### 5. Smoke-test the fitness locally

Copy `data/train_clean.csv` and `data/test_ids.csv` into a temporary folder and
call `FitnessClass(folder).calculate_fitness(chromosome)` on one chromosome.
Expect a finite score between 0 and 1 and 5,628 training rows. A random list
scores about 0.27; logistic regression about 0.76.

### 6. Run the search through the API

```bash
python earth/run_search.py
```

It uploads `train_clean.csv` + `test_ids.csv`, launches with the UI run's GA
settings, polls until Earth stops, and writes `work/optimization/earth_ids.json`
and `work/optimization/champion_chromosome.json`. Watch the generations in the
Earth UI.

### 7. Read the champion

Open both JSON files. Check `test_ids_uploaded` is `true` in `earth_ids.json`;
if it is `false`, the search trained on the 10 shared customers. Write down the
champion's model family, features, and per-fold hit rates.

### 8. Re-check on fresh split seeds

The search score is optimistic: Earth picked the best of many candidates on the
same five folds. Re-score the champion and the logistic-regression baseline on
`train_clean.csv` with new fold seeds. Keep the champion only if it still beats
the baseline.

### 9. Score once on the test set

Fit the champion and the baseline on all of `train_clean.csv` and score both
once on `data/test_clean.csv`. Search score, fresh-seed score, and test score are
different numbers.

### 10. Report

Write `work/delivery/report.md`: framing, baseline, Earth ids, champion
configuration, search vs fresh-seed vs test hit@400, and a conclusion.

## Working with your coding agent

You own problem meaning, the feature boundary, the metric, what Earth may change
vs what stays fixed, and whether the champion held up. The agent may inspect
files, implement code, run checks, and draft documentation. See
[context/workshop_pathway.md](context/workshop_pathway.md).

## Expected outputs

| After | Under `work/` |
|-------|----------------|
| Look at the data | Completed `framing.md` |
| Run the search | `optimization/earth_ids.json`, `optimization/champion_chromosome.json` |
| Re-check / test | Fresh-seed and test hit@400 for champion and baseline |
| Report | `delivery/report.md` |

## Troubleshooting

- Login name is often the part before `@` in `EARTH_USER`
- Fitness `score` must be finite and strictly positive (`max(score, 1e-9)`)
- Enum genes need `crossover: {type: error}`
- Upload only `train_clean.csv` and `test_ids.csv` to Earth — never `test_clean.csv`
- `feature_mask` positions must match the `FEATURES` list in `earth/fitness.py`

## Workshop state management

Branches, tags, and teacher vs student changes:
[context/WORKSHOP_STATE_MANAGEMENT.md](context/WORKSHOP_STATE_MANAGEMENT.md).

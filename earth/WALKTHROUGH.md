# Walkthrough — what is this search doing?

Read `earth/chromosome.yaml` and `earth/fitness.py` with these questions. Try each
one by eye first, then check your answer with your agent. Write short answers;
you will need them for Step 3.

## The chromosome (`earth/chromosome.yaml`)

1. Under `chromosome.content`, list the genes. Which are enums, ints, floats,
   bools, and which is an array?
2. `feature_mask` has 19 bools. Which list in `fitness.py` gives each position
   its meaning? What happens if the YAML says 18?
3. `model_family` picks one of three models. Which genes does each family use,
   and which genes are ignored when, say, `logistic_regression` is chosen?
4. Some genes are exponents (`lr_C_exponent`, `rf_min_samples_leaf_exponent`,
   `xgb_learning_rate_exponent`, ...). What real values do their ranges map to,
   and why search on a log scale?
5. Why do all enum genes have `crossover: {type: error}`?
6. The `ai1` block holds the GA settings. In your own words: what are
   `population_size`, `elite_percentage`, `mutation_percentage`,
   `max_stagnation_loops`, and `generation_to_start_check_steady_state`?
   Which of them does `run_search.py` override for class, and with what?

## The fitness (`earth/fitness.py`)

1. Find the `CONTRACT` block. What is the label, the positive class, and the
   ordered feature list?
2. `FitnessClass.__init__` runs once per worker. What does it load, what does it
   drop (`test_ids.csv`), and why are the folds built only once?
3. Walk through `_score` for one chromosome: which features are kept, how the
   pipeline is built, and how hit@400 is computed from the 5 folds.
4. Why `TOP_K = CAPACITY // CV_FOLDS`? What does 80 mean for the business?
5. What happens if every `feature_mask` flag is false?
6. What does Earth see when a chromosome fails to score?
7. What is in `scalars` and `rows`, and where do you see them after a run?

## Compare with your run1 champion

Open `work/runs/run1/champion_chromosome.json`.

- Which model family won? Which features did it keep and drop?
- How much do the 5 per-fold hit rates vary? Is the winner clearly better than
  logistic regression (about 0.76)?
- Which genes in the champion had no effect on its score?

## Step 3 — ideas for one chromosome change

Pick one, predict what will happen, then run.

- Remove a model family from `model_family.values` (e.g. keep only the trees).
- Narrow or widen one range (e.g. `rf_n_estimators` 100–200, or deeper
  `xgb_max_depth`).
- Remove an enum option (`scaler: [none]`, `encoding: [onehot]`).
- Change how fast the GA moves: `mutation.percentage_to_mutate`, or `ai1`
  `elite_percentage` / `mutation_percentage`.
- Population: pass `--pop` to `run_search.py` (the YAML value is overridden).

Watch out:

- Do not change the `feature_mask` size unless you also change `FEATURES` in the
  fitness (that is a Step 4 change).
- Enum values must be ones the fitness knows (`MODEL_FAMILIES`, `SCALERS`, ...).
- Always run `python earth/check_local.py --chromosome <your copy>` first.

## Step 4 — ideas for one fitness change

- `CAPACITY`: a team that can make 200 or 800 calls a month.
- `CV_FOLDS`: 3 or 10 folds (changes `TOP_K` too).
- Score the mean minus the fold std, to prefer stable champions.
- Drop a feature from `FEATURES` (and shrink `feature_mask` in a chromosome copy
  to match, then pass both `--chromosome` and `--fitness`).

Any fitness change changes what the score means: run3 numbers are not directly
comparable with run1 or run2.

# Formulation (Step 5)

Earth searches over **how the model is built**. What the campaign is worth, which columns are allowed, and how many clients are called are decided outside the search (`framing.md`, `design.md`).

Starting point from Step 4: logistic regression with default settings earns €1,489 per 1,000 (score 0.220). Target: ≥ €1,790 per 1,000 (score ≥ 0.264).

## What Earth may change (one line per gene: name, type, range or values, why)

| Gene | Type | Range / values | Why | Read in `fitness.py` |
|---|---|---|---|---|
| `model_family` | enum | `logistic_regression`, `xgboost` | LR is the baseline and linear. XGBoost can learn what LR misses: the U-shaped `age` and interactions such as job × contact. | `build_pipeline`: picks which model is created. |
| `lr_C_exponent` | float | −3 to 2 (C = 10^x, 0.001 to 100) | Regularization strength. The baseline used C = 1; with ~30 one-hot columns and 900 positives, more or less shrinkage may rank better. Log scale, because C matters by orders of magnitude. | `build_pipeline`, only when `model_family = logistic_regression`. |
| `xgb_max_depth` | int | 2 to 6 | How complex the interactions can be. Deeper trees overfit 900 positives. | `build_pipeline`, only when `model_family = xgboost`. |
| `xgb_n_estimators` | int | 50 to 400 | Number of trees. Together with the learning rate, sets how much the model learns. | `build_pipeline`, only for `xgboost`. |
| `xgb_learning_rate_exponent` | float | −2 to −0.5 (rate = 10^x, 0.01 to 0.32) | Step size of boosting. Small rates need more trees; the GA explores the pair. | `build_pipeline`, only for `xgboost`. |
| `class_weight_balanced` | bool | true / false | Upweights the 11% subscribers. It can change the ranking at the top of the list, which is where the profit is. The probabilities shift, but the call list is a top share, so the shift does not change how many we call. | `build_pipeline`: LR `class_weight="balanced"`; XGBoost `scale_pos_weight = negatives / positives` computed from `y_fit`. Used by both families. |
| `pdays_flag` | bool | true / false | Adds `contacted_before = (pdays != 999)`, the only allowed form of `pdays` (see `framing.md`). It mostly repeats `poutcome`, so the GA tests whether it helps. | `FitnessClass.__init__` creates the column once; `build_pipeline` adds it to the input columns when true. |

Genes with no effect for some candidates: the `lr_*` gene does nothing for XGBoost, and the `xgb_*` genes do nothing for LR. That is expected; it means some mutations are neutral.

Not genes, on purpose:
- **Economic columns, `month`, `day_of_week`, `campaign`, `duration`, `contact_order`.** Outside the feature boundary (`framing.md`). A gene that switches them on would let the search pick up the time period, which the random split rewards and the next campaign will not.
- **How many clients to call.** See below.

## What stays fixed, and why

| Fixed | Value | Why |
|---|---|---|
| Money | €10 per call, €70 per subscription | Given by the business (`PROJECT_BRIEF.md`). A gene would let the search change the problem instead of solving it. |
| Call-list rule | Top share; the share is the most profitable top-N on the training part's inner 3-fold out-of-fold probabilities | If Earth could set how many to call, it would tune the cut-off to the validation folds' labels, the leak `design.md` rules out. |
| Folds and seed | 5 stratified outer folds, 3 inner folds, seed 42, created once | Every candidate and the baselines are scored on the same rows, so scores compare. |
| Feature boundary | Client profile, `previous`, `poutcome`, `contact` (+ the `pdays` flag) | Only what is known before the campaign starts (`framing.md`). |
| `unknown` handling | Kept as its own category | It carries information (`framing.md`, EDA). |
| Score | mean profit per 1,000 / 6,765, floored at 1e-9 | Normalized profit: share of the maximum attainable profit (`design.md`). |
| Data | `train.csv` only | `test.csv` is read once, in Step 9. |

## Run estimate (Step 6): time per fitness call, generations, workers, expected minutes
To fill in Step 6, after timing one fitness call with `python earth/check_local.py` (one call = 20 model fits: 5 outer folds × (3 inner + 1 refit)).

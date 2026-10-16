# Workshop 1 report — Telco churn classifier

## 1. Framing

- **Goal:** flag customers of a fictional telecom who are at risk of leaving. The
  flag feeds a later retention process; this work stops at the flag.
- **Task:** binary classification, one row per customer. Positive class
  `Churn Value == 1` (26.5% of customers).
- **Data:** the five-table IBM module under `data/` (demographics, location,
  services, status), joined 1:1 on `Customer ID` → 7,043 rows. The consolidated
  `Telco_customer_churn.xlsx` was not used. It has the same IDs and labels but a
  different schema (renamed columns, missing `Age`, `Offer`, `Internet Type`, …).
- **Workshop data assumption:** the dataset is a cross-section, not a real
  prediction snapshot. We treat the selected demographic and service fields as
  known at prediction time and `Churn Value` as the later outcome. A production
  project would need event-time validation.
- **Feature boundary:** 27 features (5 demographic, 22 service). Excluded: IDs and
  constants, high-cardinality geography, target aliases, post-outcome fields
  (`Churn Category`, `Churn Reason`), model outputs (`Churn Score`, `CLTV`),
  `Satisfaction Score`, age restatements and duplicate money fields.
  Full list: `work/framing.md`.
- **Metric contract:** binary F1 for the positive class at threshold 0.5,
  `zero_division=0`, reported with precision, recall and the confusion matrix.
- **Protocol:** stratified 80/20 split, seed 42 → `train.csv` (5,634) and
  `holdout.csv` (1,409), both at 26.5% churn. Baseline and Earth used a stratified
  80/20 `inner_train` / `validation` cut of `train.csv` (4,507 / 1,127).
  Split metadata with ID hashes: `work/exploration/split_metadata.json`.
- **Success rule:** prefer the champion only if its holdout F1 is at least the
  baseline holdout F1.

## 2. Baseline

`work/modeling/baseline.py`, fixed before the search:

- numeric: median imputation + standard scaling
- categorical: `"None"` fill + one-hot (`handle_unknown="ignore"`)
- `LogisticRegression(penalty="l2", solver="lbfgs", C=1.0, max_iter=1000)`

| Validation | F1 | Precision | Recall | tn / fp / fn / tp |
|------------|----|-----------|--------|-------------------|
| Baseline | 0.6887 | 0.682 | 0.696 | 731 / 97 / 91 / 208 |

## 3. Formulation

`work/modeling/chromosome.yaml`, reduced from `context/template_churn/`. Rationale:
`work/modeling/formulation.md`.

| Earth may change | Space | Baseline value |
|------------------|-------|----------------|
| `scaling_method` | none / standard / minmax / robust | standard |
| `imbalance_method` | none / class_weight_balanced | none |
| `logistic_regression.log10_C` | [-3, 2] → C in [0.001, 100] | 0 (C = 1) |
| `logistic_regression.penalty_solver` | l2_lbfgs / l1_liblinear / elasticnet_saga | l2_lbfgs |
| `logistic_regression.l1_ratio` | [0, 1] (elastic net only) | — |

**Fixed:** model family, feature set, imputation and encoding, `max_iter`,
threshold 0.5, metric, the `inner_train` / `validation` cut, seed 42. The holdout
was never uploaded.

**Packaging:** `work/modeling/fitness.py` scores validation F1 from the uploaded
CSV. The local smoke test (`work/modeling/smoke_test.py`) reproduced the baseline
F1 exactly from the baseline chromosome. It scored 26 valid chromosomes and
handled malformed ones without raising. Earth's validator accepted the chromosome,
and its negative control was rejected.

## 4. Earth experiment

Launched with `earth/run_search.py`. Ids are in `work/optimization/earth_run.json`.

| | |
|---|---|
| Experiment id | `195f2e1d3de244f29d2ef20146f3ae3f` |
| Project id | `61db1494b8fe42a78980a4ea9c4eb9a6` (`telco-churn-w1-20261016-1158`) |
| Dataset id | `4c24e13b-1b19-41d2-97a8-c34a0bce1621` (`train.csv` only) |
| Settings | population 30, 4 fitness units, 30 min cap, stagnation 10 |
| Outcome | COMPLETED, 30 generations, 5 min 16 s |

The best fitness reached 0.6992 in the first two generations and never improved.
The population average stayed around 0.67–0.69. Most configurations in this space
score about the same.

## 5. Champion configuration

From `work/optimization/champion.json`:

| Gene | Value |
|------|-------|
| `scaling_method` | standard |
| `imbalance_method` | none |
| `penalty_solver` | elasticnet_saga |
| `log10_C` | -0.862 (C = 0.137) |
| `l1_ratio` | 0.486 |

| Validation | F1 | Precision | Recall | tn / fp / fn / tp |
|------------|----|-----------|--------|-------------------|
| Champion | 0.6992 | 0.703 | 0.696 | 740 / 88 / 91 / 208 |

Rescoring the champion locally on `train.csv` gave exactly the same numbers.

## 6. Holdout metrics

`work/delivery/holdout_validation.py` refit both models on all of `train.csv` and
scored them once on `holdout.csv`. Results: `work/delivery/holdout_metrics.json`.

| Holdout (1,409 rows) | F1 | Precision | Recall | tn / fp / fn / tp |
|----------------------|----|-----------|--------|-------------------|
| Baseline | **0.7003** | 0.735 | 0.668 | 945 / 90 / 124 / 250 |
| Champion | 0.6854 | 0.722 | 0.652 | 941 / 94 / 130 / 244 |

| F1 | Validation (search) | Holdout |
|----|---------------------|---------|
| Champion − baseline | +0.0105 | −0.0149 |

**Protocol note:** during step 6, a local re-check of the champion was pointed by
mistake at a folder containing `holdout.csv`. The fitness loader fit and scored
the champion on an 80/20 cut of the holdout and printed F1 0.658. The check was
redone on `train.csv` only. No choice depended on that number: the champion was
already fixed by Earth. The holdout comparison above is the only planned holdout
read.

## 7. Conclusion

**Keep the baseline.** The champion's holdout F1 (0.6854) is below the baseline's
(0.7003), so by the success rule the champion is not preferred.

The search improved validation F1 by about 0.01, but the gain reversed on the
holdout. With 1,127 validation rows and about 300 positives, differences of
±0.01–0.015 F1 are within noise. The flat best-fitness curve and the narrow
population spread show this space has little real headroom. The GA selected the
configuration that happened to fit that one validation cut best.

Logistic regression on these 27 features reaches about 0.69–0.70 F1 at threshold
0.5 almost regardless of scaling, regularisation or penalty. The workshop goals
held: the holdout stayed untouched until delivery, the baseline was independent of
the search, and the protocol caught a validation gain that didn't generalize.

## 8. If you ran a second optimization experiment, what additional decision would you allow Earth to evolve?

**The decision threshold**, together with a more robust fitness.

- At 26.5% positives, the default 0.5 threshold is arbitrary for F1. On both
  validation and holdout the models are more precise than they are sensitive (holdout
  precision 0.735 vs recall 0.668). That suggests a lower threshold would trade
  some precision for recall and could raise F1. The threshold is a real decision
  the current chromosome holds fixed. A one-float gene, for example
  `threshold` in [0.2, 0.6], is a small change to the formulation.
- Scoring it on a single validation cut would repeat this run's problem, and more
  so, because a threshold fits noise easily. Fitness should become the mean F1
  over stratified k-fold cross-validation within `train.csv`, for example 5 folds,
  with the same fixed seed. The holdout stays untouched until delivery.

This changes the metric contract, which fixes the threshold at 0.5. The
contract would have to be updated before the second experiment, not after it.

# Project context — S4 churn search through the Earth API

## Business frame

A fictional telecom has a retention team that can make **400 calls a month**.
The model ranks customers by churn risk; the team calls the top 400. This
session stops at the ranked list. It does not design the retention offer,
estimate uplift, or score profitability.

## Data assumption

The IBM dataset is a single snapshot with no dates. We treat the 19 feature
columns as known at the time of the call list and `Churn` as the outcome to
predict. A production churn project would need explicit event-time validation.

## Definitions

| Item | Choice |
|------|--------|
| Unit of analysis | One customer account (`customerID`) |
| Label | `Churn == "Yes"` |
| Modeling source | `data/train_clean.csv` (cleaned in S1/S2: duplicates removed, blank `TotalCharges` → 0, `LastContactReason` dropped as a leak) |
| Metric | **hit@400**: share of the 400 highest-ranked customers who actually churn. With 5-fold stratified CV (seed 42), each validation fold gets 400 / 5 = 80 calls; the score is the mean hit rate over the folds. |
| Why not F1 / AUC | Capacity is fixed, so the task is to rank and fill 400 slots. In S3, AUC tied the model families while hit@400 separated them. |
| Reference numbers | On `train_clean.csv` (5,628 rows after dropping the 10 test-shared IDs): random list ≈ 0.27, logistic regression ≈ 0.76, gentle boosting ≈ 0.81 |
| Split | Fixed in S1/S2. `train_clean.csv` for search and checks; `test_clean.csv` is the locked test set, scored once at the end. `test_ids.csv` (IDs only) is uploaded with train so the fitness drops the 10 customers who are also in test. |
| Success | The champion beats the logistic-regression baseline on the same folds, still beats it on fresh fold seeds, and holds on the test set. |

## Feature boundary

**Features (19, in `feature_mask` order):** `gender`, `SeniorCitizen`,
`Partner`, `Dependents`, `tenure`, `PhoneService`, `MultipleLines`,
`InternetService`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`,
`TechSupport`, `StreamingTV`, `StreamingMovies`, `Contract`,
`PaperlessBilling`, `PaymentMethod`, `MonthlyCharges`, `TotalCharges`.

**Never features:** `customerID` (identifier), `Churn` (label).
`LastContactReason` was removed in S1 as a leak and is not in these files.

Earth may switch features off through `feature_mask`; it cannot add columns.

## What Earth may change

Defined in `earth/chromosome.yaml`: the feature mask, encoding (one-hot /
ordinal), scaler, class weight, model family (logistic regression / random
forest / xgboost), and each family's hyperparameters. Fixed: the folds, seed,
capacity (400), and the metric.

## Deliverable

A short report with framing, baseline, Earth experiment ids, champion
configuration, hit@400 on search folds, fresh seeds and test, and a conclusion.

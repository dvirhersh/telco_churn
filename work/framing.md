# Framing (fill during Step 1)

## Goal
Build a classifier that flags customers of a fictional telecom who are at risk of leaving. The flag feeds a later retention process. This workshop stops at the flag: no retention offer design, no uplift estimate, no profitability scoring.

## Prediction task and positive class
- Unit of analysis: one customer (`Customer ID`) in the IBM cross-sectional dataset.
- Task: binary classification.
- Target: `Churn Value`. Positive class is `Churn Value == 1` (customer churned).
- Modeling source: the five-table module under `data/` (demographics, location, services, status; population optional). The consolidated `Telco_customer_churn.xlsx` is not the modeling source.

## Workshop data assumption (restate in your own words)
The IBM dataset is a snapshot of customers, not a real history of what was known before each customer left. For this workshop we pretend that the chosen demographic and service attributes were known at prediction time, and that `Churn Value` is the outcome that happened afterwards. Fields that record the outcome, or that are suspiciously tied to it, are excluded. We accept this simplification so we can focus on the DS-to-Earth pathway. A production churn project would need proper event-time validation (features as of a cutoff date, outcome measured after it).

## Metric contract
- Metric: binary F1 for the positive class at threshold 0.5, with `zero_division=0`.
- Why F1: it combines precision and recall into one scalar, which suits GA fitness. No real business cost model exists in this exercise.
- Always report precision, recall and the confusion matrix next to F1.
- Success: prefer the champion only if its holdout F1 is at least the baseline holdout F1. Reproducibility and an untouched holdout matter more than an external F1 target.

## Feature boundary (in / out)
Confirm this default before modeling.

**Out**
- IDs / constants: `Customer ID`, `Count`, `Quarter`, `Country`, `State`
- High-cardinality geography: `City`, `Zip Code`, `Lat Long`, `Latitude`, `Longitude`
- Target aliases: `Churn Label`, `Churn Value`, `Customer Status`
- Post-outcome: `Churn Category`, `Churn Reason`
- Target-adjacent / model outputs: `Churn Score`, `CLTV`
- `Satisfaction Score` (temporal availability not established; near-deterministic with target)
- Age restatements: `Under 30`, `Senior Citizen`
- Duplicate / restating money fields: `Referred a Friend`, `Total Revenue`, `Total Refunds`, `Total Extra Data Charges`, `Total Long Distance Charges`

**In**
- Demographics: `Gender`, `Age`, `Married`, `Dependents`, `Number of Dependents`
- Services: `Tenure in Months`, `Number of Referrals`, `Offer`, `Phone Service`, `Avg Monthly Long Distance Charges`, `Multiple Lines`, `Internet Service`, `Internet Type`, `Avg Monthly GB Download`, `Online Security`, `Online Backup`, `Device Protection Plan`, `Premium Tech Support`, `Streaming TV`, `Streaming Movies`, `Streaming Music`, `Unlimited Data`, `Contract`, `Paperless Billing`, `Payment Method`, `Monthly Charge`, `Total Charges`

## Fixed protocol (seed, splits, threshold)
- Seed: `random_state=42`.
- Split: stratified 80/20 into `train.csv` and `holdout.csv`.
- Earth and the baseline cut `inner_train` / `validation` from `train.csv` only.
- `holdout.csv` is scored once, at the end. The word "test" is not used for a split.
- Decision threshold: 0.5.

## Will we optimize with Earth? Why?
Yes. After a baseline is fixed, Earth searches the modeling configuration with binary F1 on `validation` as GA fitness, using only `train.csv`. The champion is compared to the baseline on the untouched holdout. Earth is only kept if holdout F1 is at least the baseline's.

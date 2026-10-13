# Project context — Workshop 1 churn classifier

## Business frame

A fictional telecom wants a model that flags customers at risk of leaving.
The score is an input to a later retention process. This workshop stops at the
flag. It does not design the retention offer, estimate uplift, or score
profitability.

## Workshop data assumption

The IBM dataset is a cross-sectional teaching dataset rather than a true
historical prediction snapshot. For Workshop 1, we treat selected demographic
and service attributes as information available at the prediction point and
`Churn Value` as the future binary outcome. Known outcome fields and suspicious
target-adjacent fields are excluded. This assumption keeps the exercise focused
on the DS-to-Earth pathway; a production churn project would require explicit
event-time validation.

## Definitions

| Item | Choice |
|------|--------|
| Unit of analysis | One customer (`Customer ID`) in this cross-section |
| Prediction task | Binary classification under the workshop data assumption |
| Positive class | `Churn Value == 1` |
| Modeling source | Five-table module under `data/` (demographics, location, services, status). Population is optional. The consolidated `Telco_customer_churn.xlsx` is **not** the modeling source. |
| Metric contract | Binary F1 for the positive class at threshold 0.5 (`zero_division=0`). F1 is selected because it combines precision and recall into one scalar suitable for GA fitness. No real business cost model is available in this exercise. Report precision, recall, and the confusion matrix beside F1. |
| Split | Stratified 80/20 → `train.csv` and `holdout.csv`, `random_state=42`. Earth and the baseline cut `inner_train` / `validation` from `train.csv` only. `holdout.csv` is scored once at the end. Workshop 1 does not use the word *test* for a split. |
| Success | Prefer the champion only when its holdout F1 is at least the baseline holdout F1. Reproducibility and an untouched holdout matter more than an external F1 target. |

## Default feature boundary (facilitator recommendation)

Students confirm this before modeling.

**Exclude**

- IDs / constants: `Customer ID`, `Count`, `Quarter`, `Country`, `State`
- High-cardinality geography: `City`, `Zip Code`, `Lat Long`, `Latitude`, `Longitude`
- Target aliases: `Churn Label`, `Churn Value`, `Customer Status`
- Post-outcome: `Churn Category`, `Churn Reason`
- Target-adjacent / model outputs: `Churn Score`, `CLTV`
- `Satisfaction Score` — temporal availability is not established, and its near-deterministic relationship with the target makes it inappropriate for this workshop
- Age restatements: `Under 30`, `Senior Citizen`
- Duplicate / restating money fields for Workshop 1: `Referred a Friend`, `Total Revenue`, `Total Refunds`, `Total Extra Data Charges`, `Total Long Distance Charges`

**Include (default)**

- Demographics: `Gender`, `Age`, `Married`, `Dependents`, `Number of Dependents`
- Services: `Tenure in Months`, `Number of Referrals`, `Offer`, `Phone Service`, `Avg Monthly Long Distance Charges`, `Multiple Lines`, `Internet Service`, `Internet Type`, `Avg Monthly GB Download`, `Online Security`, `Online Backup`, `Device Protection Plan`, `Premium Tech Support`, `Streaming TV`, `Streaming Movies`, `Streaming Music`, `Unlimited Data`, `Contract`, `Paperless Billing`, `Payment Method`, `Monthly Charge`, `Total Charges`

## Deliverable

A short report with framing, baseline, formulation, Earth experiment ids,
champion configuration, holdout metrics, a conclusion, and an answer to:
“If you ran a second optimization experiment, what additional decision would
you allow Earth to evolve?”

# Formulation (Step 4)

## Valuation genes (name, type, range, why)

| Gene | Type | Range | Why |
|------|------|-------|-----|
| `w_xgb` | float | 0–1 | Blend of XGBoost and ridge: the baseline uses one model only |
| `ridge_alpha` | float | 0.3–100 | Ridge strength |
| `log_price` | bool | | Errors in % rather than $; log-ridge broke on the baseline, let the search decide |
| `drop_big_houses` | bool | | Train without homes > 4,000 sq ft (the Edwards outliers) |
| `use_quantile` | bool | | Train XGBoost for a lower quantile: a built-in cautious value |
| `quantile_alpha` | float | 0.15–0.5 | Which quantile (only read when `use_quantile`) |
| `use_age`, `use_location`, `use_basement_garage`, `use_extras` | bool | | Feature groups on/off; quality and size always on |
| `xgb.n_estimators` | int | 200–800 | Number of trees |
| `xgb.max_depth` | int | 2–6 | Tree depth |
| `xgb.learning_rate` | float | 0.02–0.15 | Step size |
| `xgb.subsample`, `xgb.colsample_bytree` | float | 0.6–1.0, 0.4–1.0 | Row / column sampling |

Ranges from HINTS.md; they contain the baseline's best model (depth 4, 700 trees, lr 0.03).

## Pricing-policy genes (name, type, range, which homes it changes the offer for)

margin = base + k_disagree × disagreement + segment adjustments; no offer when a stop rule fires.
Disagreement = |xgb − ridge| / value.

| Gene | Type | Range | Changes the offer for | Why (Gate 3) |
|------|------|-------|----------------------|--------------|
| `base_margin` | float | 0.05–0.30 | Every home | The classic policy; baseline best is 0.18 |
| `k_disagree` | float | 0–2 | Homes where the two models disagree | Disagreement signals an uncertain value |
| `abstain_disagree` | float | 0.05–0.50 | No offer above this disagreement | Very unsure = don't buy |
| `max_offer_value` | float | 200k–500k | No offer when the predicted value is above it | Expensive homes: few training examples, large errors |
| `adj_high_tier` | float | −0.05–+0.10 | Predicted value > $300k | Same, but a softer response than no offer |
| `adj_qual_extreme` | float | −0.05–+0.10 | `Overall Qual` ≤ 4 or ≥ 9 | Rare quality levels are hard to price |
| `adj_age_old` | float | −0.05–+0.10 | Built before 1920 | Very old homes vary widely |

Adjustments are small so the search does not waste time on policies that never buy or always lose.
Total: 16 valuation + 7 policy genes = 23.

## What stays fixed, and why

- **Market rule** (2–20% flexibility, 5% costs, $500k cap, 0.5 risk weight): it is the business, not a choice.
- **Three past-year folds** (2007, 2008, 2009): same evaluation for every candidate and the baseline.
- **Feature boundary** (no `Sale Type`, `Sale Condition`, `Mo Sold`, `Yr Sold`): not known at listing.
- **The 2010 listings**: never used in the search.

## Run estimate (Step 5): seconds per fitness call, population 30, 15 workers, expected minutes

About 2–3 s per fitness call (`earth/check_local.py`, mid-range genes). Population 30 on 15 workers is
2 rounds per generation, so 80 generations take about 3 s × 2 × 80 ≈ 8 min, well under the 15-minute
class cap. The largest models in the ranges (800 trees, depth 6) are slower, so expect a bit more.

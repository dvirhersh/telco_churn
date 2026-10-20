# Evaluation design (Steps 2–3)

## How a candidate is scored (years, what is fit where, what is offered on)

A candidate is a value model plus a pricing policy. It is scored on three past years, each one an
expanding window over `work/exploration/train.csv`:

| Fold | Fit the value model on | Make offers on |
|------|------------------------|----------------|
| Y = 2007 | 625 sales of 2006 | 694 sales of 2007 |
| Y = 2008 | 1,319 sales of 2006–2007 | 622 sales of 2008 |
| Y = 2009 | 1,941 sales of 2006–2008 | 648 sales of 2009 |

In each fold the model predicts the value of every home in year Y, the policy turns that into an offer
(or no offer), and the market rule (`earth/ibuyer_market.py`) gives the expected profit and losses using
the real `SalePrice` as the true value. The three folds are added up: 1,964 offers in total. Features are
the columns inside the feature boundary (`work/framing.md`); `Yr Sold` is used only to split the folds.


## Why past years and not a random split

- **It is the real question.** In early 2010 we have sales up to 2009 and must price homes we have never
  seen, later in time. Fitting on earlier years and offering on a later one is the same situation, three
  times over.
- **A random split leaks the future.** It trains on 2009 sales to price 2007 homes, so the model sees
  prices from after the offer date, including neighbours sold later and market moves we could not know.
  The error it reports would be too optimistic.
- **The housing mix changes year to year.** New homes (`Partial` sales) fell from about 90 a year in
  2006–07 to about 28 in 2008–09. A forward split tests whether the model and policy still work when the
  mix shifts, which a random split hides by mixing the years.
- **Three years, not one,** so a policy that only works in one market (for example 2007, before the
  crash) does not win. Prices were flat (medians $160–165k), so the main risk is the mix, not inflation.

Cost: the 2007 fold trains on one year only (625 sales), so it is harder than the others. That is
fine: it is the same handicap for every candidate.


## The 2010 test: what it is, who scores it

The 341 homes listed in Ames from January to July 2010 (`data/ames_2010_listings.csv`), with features
and `ListingID` but no price. The final champion and the classic baseline each make one offer (or none)
per listing, trained on all of 2006–2009. The teacher holds the 2010 sale prices and releases them at
the end of the lab; we then score both sets of offers once with `earth/score_2010.py`, under the same
market rule. Nothing is tuned on 2010: it is the only result that was never seen during the search.


## The score (Step 5): risk-adjusted dollars per listing -> fitness

`score = (risk_adj + 3000) / 6000`, floored at 1e-9. Linear, so ranking candidates by score is the
same as ranking them by risk-adjusted dollars per listing. Break-even ($0) maps to 0.5, and −$3,000 to
+$3,000 per listing maps to 0–1, which covers most candidates. The classic baseline is scored on the
same scale.

## Classic baseline (Step 3): value model, RMSE, best flat margin, risk-adjusted profit per listing, share bought
`python3 earth/classic_baseline.py` → `work/baseline/classic_metrics.json`, `offers_2010_classic.csv`.
All numbers are on the three past-year folds (2007–2009 pooled, 1,964 homes), not on 2010.

| Item | Value |
|------|-------|
| Most accurate value model | XGBoost, depth 4, 700 trees, learning rate 0.03, log price, all 75 features |
| RMSE / MAPE | **$26,954** / 8.7% (best ridge: $33,266) |
| Best flat margin | **18%** (searched 0–30% in steps of 1%) |
| Risk-adjusted profit per listing | **−$160** (profit $547, losses −$1,416) |
| Share of listings bought | **23%** |
| Per year | 2007: −$593, 2008: −$25, 2009: +$173 |
| Fitness scale | 0.4733 (break-even = 0.5) |

The classic approach loses money on the past years, even with the margin tuned on them. These scores
were used to choose the model and the margin, so they are optimistic; only the 2010 test is unbiased.

## Gate 3: what is left to gain, and where does a flat margin lose money?
**Enough to gain? Yes.** The best classic policy loses money on 2007–2009 (−$160 per listing: losses
$1,416 > profit $547). Any policy that avoids the bad deals gains.

**Where a flat margin loses:** on homes the model **overvalues**, because sellers accept those offers
(undervalued homes are just refused). A flat margin treats every home as if the model were equally
sure. Likely places: expensive homes (> $300k, few training examples), rare quality levels (≤ 4 or
≥ 9), very old homes, and homes where ridge and XGBoost disagree.

**Trap:** three huge Edwards homes (> 4,000 sq ft, 2007–08) were valued far above their sale price.
2010 has no such homes, so avoiding them flatters the past-year score; check 2009 too.

**Policy idea:** a bigger margin, or no offer, where the model is likely wrong: by disagreement, price
tier, quality and age.

# Report — Instant offers on Ames homes

## Framing (short)

For each of the 341 homes listed in Ames in 2010: make a cash offer or not, and at what price
(predicted value × (1 − margin), never above $500k). An accepted home resells at 95% of its true value,
so offers above 95% of the true value are accepted often and lose money, and offers below 80% are never
accepted. Model errors are lopsided: an overvalued home gets an offer the seller accepts (the winner's
curse), and an undervalued home only loses the deal.

We score on **risk-adjusted profit** = profit − 0.5 × |losses|, so a lost dollar counts as $1.50.
Losses are what investors judge, and they tie up capital.

**Success on the 2010 listings:** (1) at least **$1,000 per listing** more risk-adjusted profit than
the classic baseline, and (2) expected losses no larger than the baseline's. A smaller positive gain
gets the verdict "better, but not proven". Details: `work/framing.md`.

## Data, feature boundary, evaluation

**Data:** 2,589 Ames sales from 2006–2009 with prices. Median prices were flat at $160–165k, but the
mix shifted: new homes fell from about 90 a year (2006–07) to about 28 (2008–09). EDA:
`work/exploration/eda.ipynb`.

**Feature boundary:** we drop what is known only once a sale closes: `Sale Condition` and `Sale Type`
(the outcome of the deal, and missing from the 2010 listings) and `Mo Sold` (the closing month). We
also drop `Yr Sold` as a feature, because 2010 is a value the model never saw, and the identifiers.
Every column describing the house and lot is kept.

**Evaluation:** expanding past-year folds. Fit on years before Y and offer on Y, for Y = 2007, 2008
and 2009 (1,964 offers in total), scored with the fixed market rule. That is the real situation:
price later homes from earlier sales. A random split would leak future prices and hide the shifting
mix. The fitness is `(risk_adj per listing + 3000) / 6000`, with break-even at 0.5. The 2010 test is
scored once, after the teacher releases the prices. Details: `work/design.md`.

## Classic baseline

`earth/classic_baseline.py`: the most accurate model, then the best flat margin, both chosen on the
same three folds.

| Item | Value |
|------|-------|
| Value model | XGBoost, depth 4, 700 trees, lr 0.03, log price |
| RMSE / MAPE | $26,954 / 8.7% (best ridge: $33,266) |
| Best flat margin | 18% |
| Risk-adjusted profit per listing | **−$160** (profit $547, losses −$1,416) |
| Share of listings bought | 23% |
| Per year | 2007: −$593 · 2008: −$25 · 2009: +$173 |
| Fitness | 0.473 |

**Gate 3:** even with its margin tuned, the classic policy loses money, because losses outweigh profit.
A flat margin treats every home as if the model were equally sure, so it overpays where the model
overvalues: expensive homes (> $300k), rare quality levels, very old homes, and homes where ridge and
XGBoost disagree. One trap: three huge Edwards homes (> 4,000 sq ft) dominate the 2007–08 losses, and
2010 has none like them.

## Formulation (valuation genes, policy genes, fixed choices)

23 genes: 16 valuation and 7 policy. Full table with ranges and reasons:
`work/optimization/formulation.md`.

**Valuation:** the ridge/XGBoost blend weight `w_xgb`, `ridge_alpha`, `log_price`, `drop_big_houses`,
a lower-quantile XGBoost (`use_quantile`, `quantile_alpha`), four feature-group switches, and the
XGBoost settings. The ranges contain the baseline's model.

**Pricing policy:** margin = `base_margin` + `k_disagree` × |xgb − ridge| / value + segment
adjustments. The segments are high tier (> $300k), extreme quality (≤ 4 or ≥ 9) and old (built before
1920). There is no offer when the disagreement is above `abstain_disagree` or the predicted value is
above `max_offer_value`. Each gene targets one of the Gate 3 loss sources.

**Fixed:** the market rule, the three past-year folds, the feature boundary, the $500k cap. The 2010
listings are never used in the search.

## Earth run (id, settings, champion)

## Analysis (guide questions 1–4)

## 2010 prediction (written before the reveal)

## 2010 result (earth/score_2010.py): classic vs champion, profit, losses, homes bought

## Verdict against the success criterion

## The champion's price model is about as accurate as the classic one. Where did the money come from?

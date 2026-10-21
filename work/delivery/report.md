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

Run `run1`, experiment `2cdf0b49d14c4636af961cf963cfd197`. Population 30, 15 workers × 1 CPU, elite
5%, mutation 30%, genetic drift on, steady-state check from generation 30 over 20 generations. The
status was `COMPLETED` at generation 179 after about 55 minutes. The 15-minute cap was not enforced.

**Champion** (`work/runs/run1/champion_chromosome.json`):
- **Value model:** blend of 40% XGBoost (quantile α = 0.15, depth 3, 800 trees, lr 0.069) and 60%
  ridge (α = 14.4), log price, drop houses > 4,000 sq ft, all feature groups.
- **Policy:** base margin 13.9%, `k_disagree` ≈ 0, no offer above 15.6% model disagreement,
  `max_offer_value` $500k (the cap, so inactive), old homes +5.9%, extreme quality +2.3%, high tier −1.1%.

| Per listing, 2007–2009 | Classic | Champion (Earth) | Champion (local re-score) |
|------|---------|------------------|---------------------------|
| Fitness | 0.473 | 0.710 | 0.673 |
| Risk-adjusted | −$160 | +$1,263 | **+$1,038** |
| Profit / losses | $547 / −$1,416 | $1,611 / −$698 | $1,458 / −$839 |
| Share bought | 23% | 27% | 27% |
| 2007 / 2008 / 2009 | −$593 / −$25 / +$173 | +$1,322 / +$1,543 / +$929 | +$1,250 / +$1,041 / +$808 |

**Earth vs local gap.** The local re-score uses the same `fitness.py`, the same chromosome and the
library versions in `requirements.txt`, and lands $225 per listing below Earth. For random candidates
the gap is small (about ±$40, the expected worker noise). For the top candidates, all near-copies of
the champion, it is consistently −$225 to −$280. The likely reason is that the search selected the
family Earth's workers happened to score high: elites are not re-evaluated, so a lucky score stays.
This is the winner's curse again, inside the search. I use the **local numbers** below, because
`make_offers.py` also runs locally.

## Analysis (guide questions 1–4)

### 1. Did the search behave?

Best score by generation: 0.613 (gen 0) → 0.650 (10) → 0.681 (30) → 0.699 (80) → 0.709 (120) →
0.7104 (166, the last gain). There was a fast rise to about generation 40, then 36 small gains, and
then a plateau. Only 2 of 5,400 candidates hit the floor score, and 190 lost money. Already in
generation 0 the best random candidate beat the classic baseline, so the ranges themselves start in a
good region.

*Convergence:* healthy rise then plateau. The run stopped as `COMPLETED` 13 generations after the last
gain, well past the time cap, which Earth did not enforce.

### 2. Is the champion clearly best, or one of a crowd?

A crowd of near-copies. Last-generation ranks 1 / 2 / 5 / 10 score 0.7104 / 0.7104 / 0.7078 / 0.7002.
The top 10 distinct candidates of the run all lie between 0.709 and 0.710, a spread of about $6 per
listing.

| Top 5 (Earth) | Score | Base margin | Old / extreme qual / high tier | Share bought |
|------|-------|-------------|------------------------|--------------|
| 1 (champion) | 0.710 | 0.139 | +5.9% / +2.3% / −1.1% | 26.5% |
| 2 | 0.710 | 0.139 | +5.7% / +2.3% / −1.1% | 26.5% |
| 3 | 0.710 | 0.139 | +5.9% / +3.0% / −1.1% | 26.3% |
| 4 | 0.710 | 0.139 | +5.9% / +2.3% / −1.1% | 26.4% |
| 5 | 0.709 | 0.139 | +5.9% / +2.3% / −1.1% | 26.5% |

What they agree on: quantile XGBoost at α = 0.15 (the floor of its range), `drop_big_houses`,
`log_price`, `w_xgb` ≈ 0.4, base margin 13.9%, no offer above 15.6% disagreement, `k_disagree` ≈ 0, and
extra margin on old homes. The champion beats the classic baseline in every year (locally +$1,843 /
+$1,066 / +$635 for 2007 / 2008 / 2009). The gain shrinks in 2009, the year most like 2010.

### 3. Which decisions mattered?

Gene shifts from generations 0–4 to 170–179 (mean):
- **Settled:** `k_disagree` 0.76 → 0.09, `abstain_disagree` 0.28 → 0.17, `base_margin` 0.19 → 0.145,
  `quantile_alpha` 0.33 → 0.20, `max_offer_value` $346k → $486k (pushed to the cap), `n_estimators`
  490 → 730.
- **Stable from the start:** `w_xgb` stayed around 0.40 (its spread narrowed from 0.21 to 0.10).

One-flip checks (local re-score of the champion, `work/analysis/one_flip.py`):

| Switched off | Risk-adj / listing | vs champion | Losses | Share bought |
|--------------|--------------------|-------------|--------|--------------|
| — (champion) | $1,038 | — | −$839 | 27% |
| `w_xgb` = 1 (XGBoost only) | $727 | **−$311** | −$675 | 20% |
| `use_quantile` off | $874 | **−$164** | −$1,260 | 35% |
| No abstain | $884 | **−$154** | −$1,101 | 30% |
| Segment adjustments = 0 | $984 | −$54 | −$903 | 28% |
| `adj_age_old` = 0 | $984 | −$54 | −$890 | 28% |
| `adj_qual_extreme` = 0 | $1,010 | −$28 | −$878 | 28% |
| `abstain_disagree` = 0.50 | $1,036 | −$2 | −$990 | 30% |
| `k_disagree` = 0 | $1,038 | −$0.4 | −$841 | 27% |
| `drop_big_houses` off | $1,142 | +$104 | −$734 | 26% |

The ideas that earned the most:
1. **Blending ridge into the value (+$311).** XGBoost alone buys too few homes at this margin.
2. **A cautious quantile value (+$164).** Without it, the policy buys 35% of listings and losses rise
   by half.
3. **Skipping homes the models disagree on (+$154).** Most of the effect comes from the extreme cases:
   a threshold of 0.50 instead of 0.156 earns almost the same, but with higher losses.

The old-home margin adds $54. `k_disagree` is a hitchhiker: at 0.002 it does nothing, because the
abstain rule took over its job. `max_offer_value` sits at the cap and does nothing.

Locally, `drop_big_houses` *hurts* by $104. The whole difference is in 2008–09 (2007 trains on 2006,
which has no such homes). On Earth the search preferred it, which fits the gap above. This gene is
not a reliable part of the champion.

### 4. Where does the money come from?

| Per listing, 2007–2009 (local) | Classic | Champion |
|------|---------|----------|
| Profit | $547 | $1,458 |
| Losses | −$1,416 | −$839 |
| Share bought | 23% | 27% |
| MAPE | 8.66% | 8.79% |
| RMSE | $26,954 | $45,952 |
| Median valuation error | −0.2% | −1.8% |
| Overvalued by > 10% | 15.1% of homes | 10.7% of homes |

Gain by group of homes, total +$1,198 per listing:

| Homes | Count | Classic buys | Champion buys | Gain / listing |
|-------|-------|--------------|---------------|----------------|
| Models disagree > 15.6% (the champion skips them) | 199 | 38 | 0 | **+$600** |
| Everything else | 1,417 | 326 | 455 | **+$364** |
| Quality ≤ 4 or ≥ 9 | 192 | 57 | 46 | +$113 |
| Built before 1920 | 100 | 36 | 19 | +$82 |
| Sold > $300k | 56 | 4 | 8 | +$39 |

The prices are about as accurate on average (MAPE 8.8% vs 8.7%; the champion's RMSE is higher because
the quantile model deliberately undervalues some homes by a lot). What changed is *where* the errors
fall: the champion overvalues far fewer homes, and overvaluing is what loses money.

*For a business owner:* we stopped bidding on the one home in ten our two appraisers disagree about,
and that alone saves the losses that sank the old approach. On ordinary homes we value a little lower,
which lets us take a smaller cut, so we win more deals there, and we add a bigger cut on very old or
unusual homes.

## 2010 prediction (written before the reveal)

Written on 2026-10-21, before pulling the 2010 prices.

**The offers** (`earth/make_offers.py --name run1`): the champion makes offers on 314 of the 341
listings and skips 27 (8%) where the models disagree. Its average predicted value is $166,955, against
$171,287 for the classic model (2.5% lower), and the average offers are about the same ($139k vs
$140k). The classic policy offers on all 341.

**What I expect 2010 to look like:** 2009, not 2007–08. There are no Edwards-style giants, so
`drop_big_houses` does nothing, and in 2009 the champion's gain over the classic policy was the
smallest (+$635 per listing, local). Prices fell a little from 2009, so both value models, trained on
2006–09, will run slightly high. Every policy then overpays more often, and losses go up for both. The
champion should be hurt less: its valuation is already lower (the quantile model), and it skips the
most uncertain homes. The classic policy's 18% margin also protects it, though, and its winning homes
earn more per deal.

**My numbers** (risk-adjusted profit per listing):

| | Prediction | Basis |
|---|---|---|
| Classic | about −$100 (range −$400 to +$150) | +$173 in 2009, minus the effect of the price fall |
| Champion | about +$550 (range +$200 to +$850) | +$808 in 2009 (local), minus the price fall, and 341 homes is a small, noisy sample |
| Gain | about **+$650** | close to the 2009 gain |
| Losses | champion lower than classic | in every past year it lost less while buying more |
| Share bought | champion 25–30%, classic 22–26% | as in the past years |

**Against the success criterion:** I expect criterion 2 (losses no larger than the classic policy's)
to pass, and criterion 1 (+$1,000 per listing) to **fail**. The verdict I expect is "better, but not
proven". The +$1,263 that Earth showed is inflated twice over: by the search selecting lucky scores
(−$225 locally) and by the 2007–08 Edwards homes that 2010 does not have.

## 2010 result (earth/score_2010.py): classic vs champion, profit, losses, homes bought

Scored once, on the 341 listings, with the real 2010 prices and the same market rule.

| 2010, 341 listings | Classic | Champion (run1) | Difference |
|------|---------|-----------------|------------|
| Risk-adjusted profit | −$68,038 | **+$179,199** | +$247,237 |
| Per listing | **−$200** | **+$526** | **+$725** |
| Profit (net) / listing | $448 | $993 | +$545 |
| Losses / listing | −$1,296 | −$936 | $360 less |
| Homes bought (expected) | 77.4 (22.7%) | 88.7 (26.0%) | +11 homes |
| Price error | 10.1% | 10.0% | about the same |

**Prediction vs result:**

| | Predicted | Actual |
|---|---|---|
| Classic | about −$100 (−$400 to +$150) | −$200 ✓ in range |
| Champion | about +$550 (+$200 to +$850) | +$526 ✓ |
| Gain | about +$650 | +$725 |
| Losses | champion lower | ✓ −$936 vs −$1,296 |
| Share bought | champion 25–30%, classic 22–26% | ✓ 26.0% vs 22.7% |

**Three numbers, explained:**
- **Earth's past-year score (+$1,263) is the most optimistic.** The search selected it from about
  5,400 candidates, including lucky worker scores.
- **The local past-year re-score (+$1,038) still includes the 2007–08 Edwards homes.** 2010 has none.
- **2010 (+$526) is the honest one**, close to the 2009 result (+$808) after the small price fall.

Both value models were less accurate in 2010 (about 10% error, against 8.7–8.8% on the past years). The
champion's losses rose (−$936 per listing, against −$839 on the past years), but the order did not
change: the champion still makes money and the classic policy still loses it.

### From 0.710 to 0.588: how much was overfitting?

On the fitness scale, the champion's 2010 result is (526 + 3000) / 6000 = **0.588**, against **0.710**
on Earth. That is a drop of $737 per listing, in three steps:

| Step | Score | $ / listing | Drop | Overfitting? |
|------|-------|-------------|------|--------------|
| Earth, 3 past years | 0.710 | +$1,263 | | |
| Local re-score, 3 past years | 0.673 | +$1,038 | −$225 | **Yes: selection on noise.** The best of about 5,400 scores includes lucky ones, and elites are not re-scored. |
| Local, 2009 only | 0.635 | +$808 | −$230 | **Mostly yes: fit to 2007–08 quirks.** `drop_big_houses` paid off on the Edwards homes, and is worth −$104 locally. |
| 2010 test | 0.588 | +$526 | −$282 | **No: a harder year.** The classic policy fell more over the same step (+$173 → −$200, −$373). Prices fell, and price error rose to 10% for both models. |

About **$455 of the $737 is overfitting** to the past years and to the search itself. The rest is 2010
being harder for everyone.

The classic policy barely moved (0.473 → 0.467) because it tuned one number. The champion tuned 23 genes
over about 5,400 tries, so it had far more room to fit noise. Yet it still generalised: on unseen homes
it beat the classic policy by +$725 per listing, with lower losses. **The search overstated its own gain
by about half; the half that remained was real.** The gain over the classic policy went from +$1,423
(Earth) to +$725 (2010).

**What I would change in a run2 to overfit less:**
- **Hold out a year:** search on 2007–08 only, then re-score the top 10 candidates on 2009 before
  choosing the champion.
- **Re-score elites** (`recalculate_elite: true`), so a lucky score does not stay.
- **Fewer genes:** drop the ones that did nothing (`k_disagree`, `max_offer_value`), and question
  `drop_big_houses`.
- **Choose among the near-ties by their worst year**, not by the average.

*Class spread:* (fill in after the class comparison)

## Verdict against the success criterion

1. **+$1,000 per listing over the classic policy: not met.** The gain is +$725 per listing ($247k over
   the 341 listings).
2. **Losses no larger than the classic policy's: met.** They are $360 per listing lower (−$936 vs
   −$1,296), while buying 11 more homes.

**Verdict: better, but not proven**, as predicted. The champion turns a money-losing policy into a
profitable one on unseen homes, with lower losses. But the gain is below the bar I set, and it comes
from a single year of 341 homes. The direction is clear; the size is not proven.

## The champion's price model is about as accurate as the classic one. Where did the money come from?

Not from better prices. In 2010 the price errors are 10.0% vs 10.1%, and on the past years 8.8% vs
8.7%. The money came from the **decisions**, from where each policy accepts the model's mistakes:

1. **Not bidding where the model is unsure.** The champion skips the homes where ridge and XGBoost
   disagree by more than 15.6% (27 of the 341 listings in 2010). On the past years those homes were the
   classic policy's worst: −$600 per listing of the whole set, the largest single source of the gain.
2. **A cautious value, then a smaller cut.** The quantile model values homes a little low (2.5% below
   the classic model on the 2010 listings). So it overvalues fewer homes (10.7% vs 15.1% by more than
   10% on the past years), and it can take a smaller margin (13.9% vs 18%). The result: more deals on
   ordinary homes, fewer accepted overpayments.
3. **A bigger cut where homes are hard to price:** pre-1920 homes (+5.9%) and extreme quality levels
   (+2.3%).

The one-flip checks support this. Switching off the ridge blend, the quantile value or the abstain rule
costs $150–$310 per listing each. `k_disagree` and `max_offer_value` did nothing.

*In one sentence:* the classic approach asks "what is this home worth?"; the champion also asks "how
sure am I?", and bids less, or not at all, when the answer is "not very".

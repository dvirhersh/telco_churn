# Run notes

One line per run: what you changed, what you expected, what happened.

| Run | What is different | My prediction | Fitness | Risk-adj $ per listing | Share bought | What I learned |
|-----|-------------------|---------------|---------|------------------------|--------------|----------------|
| classic | best-RMSE model + flat margin | — | 0.473 | −$160 | 23% | Loses money: losses $1,416 > profit $547 per listing |
| run1 | 23 genes: blended value model + policy (disagreement, segments, abstain); pop 30, 179 gens, COMPLETED | Not written before the run (best score seen during it) | 0.710 | +$1,263 (2007 +$1,322, 2008 +$1,543, 2009 +$929) | 27% | Losses halved (−$698 vs −$1,416) while buying more. Caution moved into the value model: quantile XGBoost at α = 0.15 (range floor) and 60% ridge allow a lower base margin (13.9% vs 18%). Disagreement is used to abstain (> 0.156), not to widen the margin (k ≈ 0). `max_offer_value` sits at the $500k cap, so it is unused. 2009, the year without the Edwards homes, gains only +$756 over the classic, below the $1,000 bar. |

"""Step 7: one-flip checks, MAPE, and segment breakdown for run1 champion vs classic. Run from repo root."""
import copy
import importlib.util
import json

import numpy as np
import pandas as pd

spec = importlib.util.spec_from_file_location("fit", "work/optimization/fitness.py")
fit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fit)
F = fit.FitnessClass("work/exploration")
champ = json.load(open("work/runs/run1/champion_chromosome.json"))["chromosome"]
classic = json.load(open("work/baseline/classic_metrics.json"))

# ---- one-flip checks ----
def flip(**changes):
    g = copy.deepcopy(champ)
    for path, v in changes.items():
        d = g
        *head, last = path.split("__")
        for h in head:
            d = d[h]
        d[last] = v
    return g

flips = {
    "champion": flip(),
    "k_disagree = 0": flip(policy__k_disagree=0.0),
    "no abstain (abstain_disagree = inf)": flip(policy__abstain_disagree=1e9),
    "abstain_disagree = 0.50 (range max)": flip(policy__abstain_disagree=0.50),
    "segment adjustments = 0": flip(policy__adj_high_tier=0.0, policy__adj_qual_extreme=0.0, policy__adj_age_old=0.0),
    "adj_age_old = 0": flip(policy__adj_age_old=0.0),
    "adj_qual_extreme = 0": flip(policy__adj_qual_extreme=0.0),
    "use_quantile = off": flip(use_quantile=False),
    "w_xgb = 1 (XGBoost only)": flip(w_xgb=1.0),
    "drop_big_houses = off": flip(drop_big_houses=False),
}
rows = []
for name, g in flips.items():
    s = F.calculate_fitness(g).scalars
    rows.append({"variant": name, "risk_adj": s["risk_adj_per_listing"], "profit": s["profit_per_listing"],
                 "losses": s["losses_per_listing"], "share_bought": s["share_bought"],
                 **{k[-4:]: v for k, v in s["per_year"].items()}})
res = pd.DataFrame(rows)
res["vs_champion"] = res.risk_adj - res.risk_adj.iloc[0]
pd.set_option("display.width", 200)
print(res.round(3).to_string(index=False))

# ---- MAPE, bias, and segment breakdown on the three folds ----
cg = dict(classic["value_genes"])
margin = classic["best_flat"]["margin"]
recs = []
for (tr, va), year in zip(F.folds, fit.VALID_YEARS):
    x_tr, x_va, y_tr, y_va = F.data.iloc[tr], F.data.iloc[va], F.y[tr], F.y[va]
    cv, _, _ = fit.Valuer(cg, F.data.columns).fit(x_tr, y_tr).predict(x_va)
    hv, hr, hx = fit.Valuer(champ, F.data.columns).fit(x_tr, y_tr).predict(x_va)
    c_offer, c_make = cv * (1 - margin), np.ones(len(va), bool)
    h_offer, h_make = fit.offer_prices(champ["policy"], hv, hr, hx, x_va)
    for who, val, off, mk in (("classic", cv, c_offer, c_make), ("champion", hv, h_offer, h_make)):
        mk = mk & (off <= fit.MAX_OFFER)
        p = np.clip((fit.FLEX[1] - (1 - off / y_va)) / (fit.FLEX[1] - fit.FLEX[0]), 0, 1) * mk
        gain = y_va * (1 - fit.COST) - off
        recs.append(pd.DataFrame({
            "who": who, "year": year, "true": y_va, "value": val, "offer": off, "make": mk,
            "p": p, "profit": p * gain, "loss": p * np.minimum(gain, 0),
            "qual": x_va["Overall Qual"].to_numpy(), "built": x_va["Year Built"].to_numpy(),
            "disagree": np.abs(hx - hr) / hv}))
d = pd.concat(recs)
d["ape"] = (d.value - d.true).abs() / d.true
d["err"] = (d.value - d.true) / d.true
print("\nValue accuracy (pooled 2007-2009)")
for who, g in d.groupby("who", sort=False):
    rmse = np.sqrt(((g.value - g.true) ** 2).mean())
    print(f"  {who:9s} MAPE {g.ape.mean():.3%}  RMSE ${rmse:,.0f}  median error {g.err.median():+.2%}  "
          f"overvalued by >10%: {(g.err > 0.10).mean():.1%}")

def seg(r):
    if r.disagree > champ["policy"]["abstain_disagree"]:
        return "models disagree > 15.6% (champion abstains)"
    if r.built < 1920:
        return "built before 1920"
    if r.qual <= 4 or r.qual >= 9:
        return "quality <= 4 or >= 9"
    if r.true > 300_000:
        return "sold > $300k"
    return "everything else"

# segment by the champion's view of each home (same homes in both)
key = d[d.who == "champion"].apply(seg, axis=1).to_numpy()
n_homes = (d.who == "champion").sum()
segs = pd.Series(key)
d = d.reset_index(drop=True)
d.loc[d.who == "classic", "segment"] = segs.values
d.loc[d.who == "champion", "segment"] = segs.values
d["risk_adj"] = d.profit + fit.RISK_WEIGHT * d.loss
t = d.groupby(["segment", "who"], sort=False).agg(homes=("p", "size"), bought=("p", "sum"),
                                                  profit=("profit", "sum"), losses=("loss", "sum"),
                                                  risk_adj=("risk_adj", "sum")).unstack("who")
print(f"\nBy segment, totals over {n_homes} listings ($ per listing of the whole set)")
out = pd.DataFrame({
    "homes": t[("homes", "classic")],
    "bought classic": t[("bought", "classic")].round(0),
    "bought champ": t[("bought", "champion")].round(0),
    "risk_adj classic": (t[("risk_adj", "classic")] / n_homes).round(0),
    "risk_adj champ": (t[("risk_adj", "champion")] / n_homes).round(0),
    "losses classic": (t[("losses", "classic")] / n_homes).round(0),
    "losses champ": (t[("losses", "champion")] / n_homes).round(0),
})
out["gain"] = out["risk_adj champ"] - out["risk_adj classic"]
print(out.to_string())
print("sum of gains:", out.gain.sum())

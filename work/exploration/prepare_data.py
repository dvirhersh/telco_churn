"""Explore step: join the five-table module, profile it, freeze train/holdout.

Run from the repo root:  python work/exploration/prepare_data.py
Refuses to overwrite an existing holdout.csv (the holdout is frozen once).
"""
import hashlib
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent
SEED = 42
ID, TARGET = "Customer ID", "Churn Value"

EXCLUDE = [
    "Customer ID", "Count", "Quarter", "Country", "State",
    "City", "Zip Code", "Lat Long", "Latitude", "Longitude",
    "Churn Label", "Churn Value", "Customer Status",
    "Churn Category", "Churn Reason", "Churn Score", "CLTV",
    "Satisfaction Score", "Under 30", "Senior Citizen",
    "Referred a Friend", "Total Revenue", "Total Refunds",
    "Total Extra Data Charges", "Total Long Distance Charges",
]


def load_joined() -> pd.DataFrame:
    """Join demographics, location, services, status on Customer ID.

    Population is optional and keyed by Zip Code (a geography field we exclude),
    so it is not joined. `Count` / `Quarter` are repeated across tables; keep one.
    """
    # keep_default_na=False: "None" in Offer / Internet Type is a real category, not missing
    read = lambda n: pd.read_excel(DATA / f"Telco_customer_churn_{n}.xlsx", keep_default_na=False)
    demo, loc, svc, status = (read(n) for n in ("demographics", "location", "services", "status"))
    for name, t in (("demographics", demo), ("location", loc), ("services", svc), ("status", status)):
        assert t[ID].is_unique, f"{name}: duplicate {ID}"
    df = demo
    for t in (loc, svc, status):
        t = t.drop(columns=[c for c in ("Count", "Quarter") if c in df.columns])  # repeated across tables
        df = df.merge(t, on=ID, how="inner", validate="1:1")
    assert len(df) == len(demo), "join lost or gained rows"
    return df


def profile(df: pd.DataFrame, features: list[str]) -> dict:
    X = df[features]
    miss = X.isna().sum()
    return {
        "joined_shape": list(df.shape),
        "n_candidate_features": len(features),
        "target_counts": df[TARGET].value_counts().to_dict(),
        "target_rate": round(float(df[TARGET].mean()), 4),
        "missing": miss[miss > 0].to_dict(),
        "blank_strings": {c: int((X[c].astype(str).str.strip() == "").sum())
                          for c in X.select_dtypes("object") if (X[c].astype(str).str.strip() == "").any()},
        "dtypes": X.dtypes.astype(str).value_counts().to_dict(),
        "object_cols": X.select_dtypes("object").columns.tolist(),
        "numeric_cols": X.select_dtypes("number").columns.tolist(),
        "constant_cols": [c for c in features if X[c].nunique(dropna=False) <= 1],
    }


def main() -> None:
    df = load_joined()
    # Total Charges can arrive as blank strings for zero-tenure customers
    df["Total Charges"] = pd.to_numeric(df["Total Charges"], errors="coerce")

    missing_cols = [c for c in EXCLUDE if c not in df.columns]
    assert not missing_cols, f"exclusion list names unknown columns: {missing_cols}"
    features = [c for c in df.columns if c not in EXCLUDE]
    info = profile(df, features)
    info["features"] = features
    info["excluded"] = EXCLUDE
    print(json.dumps(info, indent=2, default=str))

    holdout_path = OUT / "holdout.csv"
    if holdout_path.exists():
        raise SystemExit("holdout.csv already exists; it is frozen. Not overwriting.")

    model_df = df[features + [TARGET]]
    train, hold = train_test_split(
        model_df, test_size=0.2, stratify=model_df[TARGET], random_state=SEED)
    train.to_csv(OUT / "train.csv", index=False)
    hold.to_csv(holdout_path, index=False)

    meta = {
        "seed": SEED, "test_size": 0.2, "stratify": TARGET,
        "train_rows": len(train), "holdout_rows": len(hold),
        "train_target_rate": round(float(train[TARGET].mean()), 4),
        "holdout_target_rate": round(float(hold[TARGET].mean()), 4),
        "train_ids_sha256": hashlib.sha256(",".join(sorted(df.loc[train.index, ID])).encode()).hexdigest(),
        "holdout_ids_sha256": hashlib.sha256(",".join(sorted(df.loc[hold.index, ID])).encode()).hexdigest(),
        "source": "five-table module (demographics, location, services, status); Telco_customer_churn.xlsx NOT used",
        **{k: info[k] for k in ("features", "excluded", "missing", "target_counts")},
    }
    (OUT / "split_metadata.json").write_text(json.dumps(meta, indent=2, default=str))
    print(f"\ntrain {train.shape}, holdout {hold.shape}")


if __name__ == "__main__":
    main()

# Formulation — what Earth may change, what stays fixed

Chromosome: [`chromosome.yaml`](chromosome.yaml). Reference consulted:
`context/template_churn/` (default chromosome, philosophy, constraints, invariants).

## Earth may change (5 genes)

| Gene | Space | Baseline value | Why it is searchable |
|------|-------|----------------|----------------------|
| `scaling_method` | `none`, `standard`, `minmax`, `robust` | `standard` | Affects regularisation and solver behaviour; no a-priori winner |
| `imbalance_method` | `none`, `class_weight_balanced` | `none` | 26.5% positives; reweighting trades precision for recall, which moves F1 at a fixed 0.5 threshold |
| `logistic_regression.log10_C` | float [-3, 2] → C in [0.001, 100] | 0 (C = 1) | Regularisation strength; log scale so the GA samples small and large C evenly |
| `logistic_regression.penalty_solver` | `l2_lbfgs`, `l1_liblinear`, `elasticnet_saga` | `l2_lbfgs` | L1 / elastic net act as implicit feature selection over the one-hot columns |
| `logistic_regression.l1_ratio` | float [0, 1] | n/a | Only active for `elasticnet_saga`; ignored otherwise |

The baseline configuration is a point inside this space, so the search can at
least recover it.

## Stays fixed

| Decision | Fixed value | Reason |
|----------|-------------|--------|
| Model family | Logistic regression | Workshop 1 keeps the ML problem simple; the baseline is logistic, so the comparison isolates configuration |
| Feature set | 27 features from `work/framing.md` | Feature boundary is a framing decision (leakage / prediction-time), not a search variable |
| Numeric imputation | median | No numeric missingness in the data; nothing to search |
| Categorical handling | `"None"` fill + one-hot, `handle_unknown="ignore"` | All categoricals are low-cardinality; ordinal codes would be meaningless for a linear model |
| `max_iter` | 1000 (fitness may raise for saga) | Convergence budget, not a modeling hypothesis |
| Decision threshold | 0.5 | Part of the metric contract |
| Metric | Binary F1, positive class, `zero_division=0` | Metric contract; fitness policy is not a gene |
| Split | `inner_train` / `validation` = stratified 80/20 of `train.csv`, seed 42 | Same cut as the baseline so fitness and baseline evidence are comparable |
| Seed | 42 | Seeds are fixed, never optimized |
| Holdout | Not uploaded, not read | Immutable holdout rule |

## Left out of the template on purpose

- Feature engineering genes (selection masks, interactions, binning, power
  transform, outlier handling)
- Per-column preprocessing arrays
- Other models (XGBoost, CatBoost, SVM) and ensemble weights
- `downsample_majority` / `target_positive_ratio`, revenue sample weighting
- `max_iter` as a gene

## Decoding rules for the fitness function

- `C = 10 ** log10_C`, clipped to [1e-3, 1e2].
- `penalty_solver` maps to `(penalty, solver)`: `l2_lbfgs` → `("l2", "lbfgs")`,
  `l1_liblinear` → `("l1", "liblinear")`, `elasticnet_saga` → `("elasticnet", "saga")`.
- `l1_ratio` is passed only for `elasticnet_saga`, clipped to [0, 1].
- `class_weight="balanced"` when `imbalance_method == class_weight_balanced`, else `None`.
- Unknown values fall back to the baseline choice. Any fit failure returns fitness 0.0.

## Search size

About 4 × 2 × 3 = 24 discrete combinations times two continuous genes. That is
small enough for one modest Earth run (population 50) to cover well.

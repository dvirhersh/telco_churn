# Template churn reference (not Workshop 1 runtime)

This folder is an unchanged copy of chromosome and fitness examples from the
Earth `churn-prediction` template. Students and coding agents may read it when
formulating a search space.

Workshop 1 does **not** run these files.

## What is here

| Path | Role |
|------|------|
| `chromosome/default_chromosome.yaml` | Full production-style search space |
| `chromosome/README.md` | Short note on that YAML |
| `fitness.py` | `FitnessCalculationResult` only |
| `project_files_template/fitness.py.template` | `FitnessClass` shape |
| `context/` | Chromosome philosophy, overview, constraints, invariants |

## What Workshop 1 borrows

- `FitnessClass(dataset_root)` loads data once; `calculate_fitness` returns `FitnessCalculationResult`
- Gene names such as `scaling_method`, `imbalance_method`, and nested `logistic_regression` / `xgboost` blocks

## What Workshop 1 leaves behind

- Ensemble weights and multi-model voting
- Per-column preprocessing arrays
- Intervention profit, precision-at-K, cost models
- Feature engineering genes (interactions, binning, selection masks)

The runnable chromosome and fitness for this workshop are created under `work/`
during the pathway (solution tag: `work/modeling/`).

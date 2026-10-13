# Binary Classifier Template – Overview

**R2 data profiling spec:** [`data_profiling_r2.md`](data_profiling_r2.md) (contract, `dataset_profile.json`, churn profiling CLI).

This template implements a reusable solution framework
for binary classification problems optimized using Earth GA.

It defines:

- Chromosome structure for binary classification
- Preprocessing pipeline generation
- Model construction and ensembling
- Generic evaluation metrics
- Fitness score computation

---

# Problem Class

The template solves:

Binary classification tasks where:

- Target variable has two classes.
- Supervised learning is applicable.
- GA optimizes model configuration and preprocessing.

Examples (non-binding):

- Churn prediction
- Fraud detection
- Risk scoring
- Eligibility classification

---

# What This Template Owns

- Chromosome → pipeline translation
- Feature preprocessing mechanics
- Model selection and hyperparameter search
- Generic evaluation logic (e.g. AUC, F1)
- Cross-validation and training loop
- **Post-experiment orchestration:** `run_post_experiment.sh` (Steps 8, 10, 12, 13) and `dataset_profile_to_csv.py` (feature analysis report); projects receive copies via `create_project.sh` / `update_project_scripts.sh`

---

# What This Template Does NOT Own

- Business cost models
- Dataset semantics
- Label meaning
- Threshold policies tied to business
- Project-specific feature exclusions

These belong to R3 (Project layer).

---

# Architectural Role

This template sits between:

- R1 (GA Contract) — execution guarantees
- R3 (Project Binding) — business semantics

It must remain reusable across multiple binary classification problems.

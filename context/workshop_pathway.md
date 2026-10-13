# Workshop pathway (minimal practices)

Full practices: [methods/PROJECT_DELIVERY_PRACTICES_ONE_PAGER.md](methods/PROJECT_DELIVERY_PRACTICES_ONE_PAGER.md).
Tabular EDA/split detail: [methods/TABULAR_EDA_AND_SPLIT_GUIDELINES.md](methods/TABULAR_EDA_AND_SPLIT_GUIDELINES.md).

Phases taught here: **Frame → Explore → Build → Optimize → Deliver**.

## Practices in this workshop

| Phase | Practice | Workshop DoD |
|-------|----------|--------------|
| Frame | Project Framing + Success Criteria | Written target, metric contract, feature boundary |
| Explore | Data Foundation | Join five tables, short EDA, freeze `train.csv` / `holdout.csv` once |
| Build | Solution Design + Baseline Evidence | Fixed logistic pipeline scored on `validation` cut from train |
| Optimize | Formulation → Packaging → Validation → Execution | Modest chromosome, local smoke test, one Earth run, champion JSON |
| Deliver | Production Packaging (narrow) | One holdout read for baseline vs champion; written report |

Skipped in Workshop 1: Deployment & Monitoring; full PMO gates; retrospective beyond a short conclusion.

## Two non-negotiable rules

1. **Immutable holdout.** `holdout.csv` is created once in Explore. Baseline, smoke test, and Earth never read it. Delivery is the only metric read.
2. **Baseline independence.** The baseline is specified and coded before search. It is not a GA champion.

Gate 3 in a real project asks whether the baseline justifies optimization spend. This class proceeds to Earth because the learning goal is the pathway.

## Agent vs student

| Student owns | Coding agent may do |
|--------------|---------------------|
| What the prediction problem means | Inspect files and schema |
| Which fields are allowed at “prediction time” (workshop assumption) | Write loaders, plots, preprocessing |
| Metric contract (F1 here) | Implement the baseline after the student defines it |
| What belongs in the chromosome vs stays fixed | Translate the formulation into YAML / fitness |
| Whether the champion generalized | Run smoke tests and Earth scripts |
| The delivery conclusion | Assemble report skeletons from artifacts |

## Split vocabulary

| Name | Role |
|------|------|
| Raw Excel under `data/` | Source tables |
| `train.csv` | Development set used for baseline and Earth |
| `inner_train` + `validation` | Stratified cut of `train.csv` for fitness / baseline evidence |
| `holdout.csv` | Final score once, at delivery only |

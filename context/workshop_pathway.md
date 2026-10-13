# Workshop pathway (minimal practices)

Full practices: [methods/PROJECT_DELIVERY_PRACTICES_ONE_PAGER.md](methods/PROJECT_DELIVERY_PRACTICES_ONE_PAGER.md).
Tabular EDA/split detail: [methods/TABULAR_EDA_AND_SPLIT_GUIDELINES.md](methods/TABULAR_EDA_AND_SPLIT_GUIDELINES.md).

Phases taught here: **Frame → Explore → Build → Optimize → Deliver**.

## Practices in this workshop

| Phase | Practice | Workshop DoD |
|-------|----------|--------------|
| Frame | Project Framing + Success Criteria | Written target, metric contract, feature boundary |
| Explore | Data Foundation | Read `train_clean.csv` with the data dictionary; the split was frozen in S1/S2 |
| Build | Solution Design + Baseline Evidence | Logistic-regression baseline scored with hit@400 on the same 5 folds |
| Optimize | Formulation → Packaging → Validation → Execution | UI chromosome + fitness, local smoke test, one API run, champion JSON |
| Deliver | Production Packaging (narrow) | Fresh-seed re-check, one test read for baseline vs champion; written report |

Skipped in this session: Deployment & Monitoring; full PMO gates; retrospective beyond a short conclusion.

## Two non-negotiable rules

1. **Locked test set.** `test_clean.csv` was frozen in S1/S2. Baseline, smoke test, and Earth never read it, and it is never uploaded. Delivery is the only metric read.
2. **Baseline independence.** The baseline is specified and coded before search. It is not a GA champion.

Gate 3 in a real project asks whether the baseline justifies optimization spend. This class proceeds to Earth because the learning goal is the pathway.

## Agent vs student

| Student owns | Coding agent may do |
|--------------|---------------------|
| What the prediction problem means | Inspect files and schema |
| Which fields are allowed at “prediction time” (workshop assumption) | Write loaders, plots, preprocessing |
| Metric contract (hit@400 here) | Implement the baseline after the student defines it |
| What belongs in the chromosome vs stays fixed | Translate the formulation into YAML / fitness |
| Whether the champion generalized | Run smoke tests and Earth scripts |
| The delivery conclusion | Assemble report skeletons from artifacts |

## Split vocabulary

| Name | Role |
|------|------|
| `data/train_clean.csv` | Development set: Earth search, baseline, fresh-seed re-checks |
| Validation folds | 5 stratified folds of train (seed 42); hit@400 = mean hit rate among the top 80 per fold |
| `data/test_ids.csv` | IDs only, uploaded with train so fitness drops the 10 customers also in test |
| `data/test_clean.csv` | Locked test set; scored once, at delivery only |

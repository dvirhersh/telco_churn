# DS Project Delivery Practices

**Version:** 0.4 (draft)
**Status:** Work Package 2 output — per [ASSIGNMENT_OBJECTIVE_SCOPE_PLAN.md](ASSIGNMENT_OBJECTIVE_SCOPE_PLAN.md)
**Supersedes:** [PROJECT_LIFECYCLE_V0.md](Archive/PROJECT_LIFECYCLE_V0.md)
**Relationship to the org standard:** this is the Tier 2 (Practices) layer under the
teamlead's DS Delivery Operating System v4.0. Tier 1 (Phases) is owned by v4.0 and
reproduced here only as the frame Practices sit inside. Tier 3 (Methodologies &
Guidelines) is linked from each Practice, not duplicated into it.

Three open items from the assignment plan are referenced inline below and marked
**(proposed)** where this document takes a position — final sign-off on anything that
amends v4.0 itself rests with the teamlead, per the plan's §6 scope note.

## Glossary

| Term | Definition |
|---|---|
| Phase | One of the 5 top-level stages of project evolution (Frame, Explore, Build, Optimize, Deliver) |
| Practice | A recurring, named unit of delivery work with inputs, outputs, and a Definition of Done |
| Methodology | A reusable scientific/engineering approach for a specific modality, engine, or goal |
| Gate | A PMO investment decision — authorize, increase, redirect, defer, or stop capacity. **Not** a quality checkpoint by itself |
| Milestone | A recorded, evidence-based achievement. **Not** an investment authorization by itself |

## 1. Delivery Phases (Tier 1 — v4.0, reproduced for reference)

`FRAME → EXPLORE → BUILD → OPTIMIZE → DELIVER`

| Phase | Question | Practices in this document |
|---|---|---|
| Frame | Why is this problem worth solving? | Project Framing, Success Criteria |
| Explore | Is there sufficient evidence for a viable solution? | Data Foundation, Solution Design |
| Build | Do we have a system that reliably works? | Baseline Evidence |
| Optimize | How can the working system perform better? | Optimization Formulation, Optimization Packaging, Optimization Validation, Optimization Execution |
| Deliver | How does the project outcome become usable value? | Production Packaging, Deployment & Monitoring, Project Retrospective |

Not a rigid state machine: a project may skip a non-applicable Practice, run several
concurrently, or return to an earlier one when new evidence changes understanding.

## 2. Milestone ↔ Gate Map (resolves open item #1 — proposed)

Every Practice below produces a Milestone (evidence record). Only five of them are
paired with a Gate (an investment decision) — this mirrors the five Gates (A–E) from
the previous version of this document one-for-one, just re-anchored to the new Practice
names.

| # | Practice | Milestone | Paired Gate? | Gate question |
|---|---|---|---|---|
| 1 | Project Framing | Problem Defined | — | — |
| 2 | Success Criteria | Success Criteria Approved *(proposed name)* | **Gate 1** | Are goals and success metrics approved? |
| 3 | Data Foundation | Data Readiness Confirmed *(proposed name)* | **Gate 2** | Does data quality/feasibility support continuing? |
| 4 | Solution Design | Approach Selected *(proposed name)* | — | — |
| 5 | Baseline Evidence | Baseline Validated | **Gate 3** | Does baseline quality justify optimization investment? |
| 6 | Optimization Formulation | Optimization Formulated | — | — |
| 7 | Optimization Packaging | Optimization Package Ready *(proposed name)* | — | — |
| 8 | Optimization Validation | Optimization Validated | **Gate 4** | Is the package ready and reproducible for significant execution? |
| 9 | Optimization Execution | Optimized Solution Selected | — | — |
| 10 | Production Packaging | Production Ready | **Gate 5** | Does the final solution meet acceptance for rollout? |
| 11 | Deployment & Monitoring | Value Delivered | — | — |
| 12 | Project Retrospective | Insights Captured *(proposed name)* | — | — |

Milestones marked *(proposed name)* are not in v4.0's own example list and are this
document's proposal to fill the gap; the other four (Problem Defined, Baseline
Validated, Optimization Formulated, Optimization Validated, Optimized Solution Selected,
Production Ready, Value Delivered) are adopted verbatim from v4.0 §5.1.

Project Retrospective has no paired Gate on purpose: by the time it runs, the project
has already reached Value Delivered (or stopped). What it feeds is *organizational*
investment — whether to promote a finding into a Methodology or Standard — which isn't a
per-project PMO Gate decision.

## 3. Practices

Each Practice below follows the org standard's Practice fields (v4.0 §4.3): purpose,
inputs, recommended work, outputs, completion criteria, anti-patterns, related
Methodologies.

---

### Phase: Frame

#### Practice 1 — Project Framing

- **Purpose:** Establish why the project exists and define its boundaries.
- **Milestone:** Problem Defined.
- **Required Inputs:** Client/business problem statement, business context.
- **Recommended Work:** Define goal, Definition of Done, risks, deliverables, timeline,
  owners. Classify project type (data modality, ML type, research/pilot/production
  intent).
- **Required Output:** Project charter.
- **Completion Criteria (DoD):**
  - Goal and DoD are written down, not implicit.
  - Project type (for example classification/regression/clustering) is recorded (drives which Tier 3 Methodologies apply).
  - Owners and timeline are named.
- **Common Anti-Patterns:** Starting data work before the goal is written down;
  treating "we understand the ask informally" as equivalent to a charter.
- **Related Methodologies:** none (modality-agnostic).

#### Practice 2 — Success Criteria

- **Purpose:** Define measurable project success.
- **Milestone:** Success Criteria Approved. **→ Gate 1**
- **Required Inputs:** Project charter.
- **Recommended Work:** Define the primary business KPI, the primary ML metric, and
  constraints (latency, cost, explainability, regulatory). Add acceptance thresholds.
- **Required Output:** Metric contract.
- **Completion Criteria (DoD):**
  - Business KPI and ML metric are both named — one without the other is incomplete.
  - Acceptance thresholds are numeric, not aspirational language.
  - Constraints that cannot be violated are listed explicitly (Principle 6).
- **Gate 1 question:** Are goals and success metrics approved to invest in Explore?
- **Common Anti-Patterns:** An ML metric with no linked business KPI; thresholds set
  after modeling has already started (reverse-engineered success).
- **Related Methodologies:** for unsupervised/no-ground-truth projects, see
  [Clustering EDA & Methodology](Methodologies_&_Guidelines/CLUSTERING_EDA_AND_METHODOLOGY.md) — an ML metric
  threshold doesn't apply without labels; an evaluation proxy must be defined instead.

---

### Phase: Explore

#### Practice 3 — Data Foundation

- **Purpose:** Establish sufficient data understanding and readiness. Merges what the
  previous version of this document split across three steps (data contract, EDA and
  profiling, split strategy) into one Practice, per v4.0's consolidated naming.
- **Milestone:** Data Readiness Confirmed. **→ Gate 2**
- **Required Inputs:** Raw datasets, metadata, column descriptions, data contract.
- **Recommended Work:**
  - *Data contract:* define target, ID columns, non-model descriptive columns, leakage
    exclusions, feature typing source of truth.
  - *EDA and profiling:* rows/cols, target balance, missingness, numeric/categorical
    distributions, feature-target correlation, inter-feature correlation, skew/outliers,
    pre-ML expectations.
  - *Split strategy:* create the constant holdout test set once (stratified for
    classification).
- **Required Output:** Data contract, EDA notebook + profile report, immutable test set
  + train set.
- **Completion Criteria (DoD):**
  - Data contract fields are all explicit (no implicit target/ID/leakage assumptions).
  - EDA covers all items above, not a partial subset.
  - **The holdout test set is created once and is never touched for search or
    optimization** *(open item #3 — the immutable-holdout rule).* It is only read again
    in Production Packaging.
  - **Exception — Split Revision:** a split may be legitimately revised when new
    understanding of the data itself emerges (e.g. a labeling error, a previously
    unknown leakage source, a population the original split didn't account for) —
    confirmed as a real pattern in project review (baranes-nv). This is **not** the same
    as re-cutting the split because a result was disappointing — that remains a
    violation. A Split Revision is a tracked event: it (1) is versioned (`split_v1`,
    `split_v2`, ...) with the reason recorded, (2) invalidates any Baseline/Optimization
    evidence collected under the prior split version, and (3) requires Gate 2 to be
    re-passed before downstream work resumes. Absent a recorded Split Revision, the
    holdout is inviolable.
- **Gate 2 question:** Does data quality and feasibility support continuing into
  Solution Design and Baseline Evidence? (Re-asked on every Split Revision.)
- **Common Anti-Patterns:** Re-cutting the holdout set because a baseline or
  optimization result was disappointing — the exact failure mode the immutable-holdout
  rule exists to prevent, and distinct from a legitimate, recorded Split Revision above;
  discovering leakage during Optimization Execution instead of here; revising the split
  without versioning it or invalidating downstream evidence.
- **Related Methodologies:** [Tabular EDA & Split Guidelines](Methodologies_&_Guidelines/TABULAR_EDA_AND_SPLIT_GUIDELINES.md),
  [Audio Data EDA & Split Guidelines](Methodologies_&_Guidelines/AUDIO_DATA_EDA_AND_SPLIT_GUIDELINES.md),
  [Audio vs. Tabular EDA](Methodologies_&_Guidelines/AUDIO_VS_TABULAR_EDA_ONE_PAGER.md),
  [Clustering EDA & Methodology](Methodologies_&_Guidelines/CLUSTERING_EDA_AND_METHODOLOGY.md) *(initial framing)*
  — adds scale-sensitivity checks, routing-covariate identification, and a
  stability-check holdout in place of the standard leakage-focused split.

#### Practice 4 — Solution Design

*New Practice, adopted from v4.0 — the previous version of this document had no
equivalent and went directly from data prep to baseline modeling. This closes that gap.*

- **Purpose:** Define the intended solution approach before committing engineering
  effort to a baseline.
- **Milestone:** Approach Selected.
- **Required Inputs:** Data contract, EDA/profile report, metric contract.
- **Recommended Work:**
  - Decide the candidate model family/families and pipeline shape appropriate to the
    project type and constraints (e.g. explainability requirements rule out black-box
    models).
  - Decide the evaluation protocol (CV scheme, holdout usage, metric aggregation) —
    this must be fixed before Baseline Evidence, not improvised per experiment.
  - Make an explicit Deterministic vs. Optimization Engineering call (Principle 4):
    is a reliable baseline sufficient, or is optimization expected to be pursued later?
    Not every project needs Optimization (Principle 5) — this is the decision point
    where that gets decided and recorded, rather than optimization happening by default.
- **Required Output:** Solution approach memo — chosen model family/pipeline shape,
  evaluation protocol, and the deterministic-vs-optimization call with rationale.
- **Completion Criteria (DoD):**
  - Evaluation protocol is written down before any model is trained under it.
  - The optimization decision is explicit and justified, not silently assumed.
- **Common Anti-Patterns:** Jumping straight to a preferred model family out of habit;
  assuming optimization is always the next step regardless of evidence.
- **Related Methodologies:** [Clustering EDA & Methodology](Methodologies_&_Guidelines/CLUSTERING_EDA_AND_METHODOLOGY.md)
  *(initial framing)* — for clustering, this Practice must also decide the assignment
  mechanism for new/incoming records, which has no supervised-learning equivalent.

---

### Phase: Build

#### Practice 5 — Baseline Evidence

- **Purpose:** Establish reproducible evidence that a viable solution exists, in a form
  appropriate to what kind of system is actually being built.
- **Milestone:** Baseline Validated. **→ Gate 3**
- **Required Inputs:** Train/test sets, solution approach memo.
- **Recommended Work:** Baseline Evidence takes one of two forms, decided in Solution
  Design:
  - **Simple-model form** (default when a non-optimized candidate exists in its own
    right): train simple baseline models (e.g. logistic regression, XGBoost) with
    minimal preprocessing, per the evaluation protocol fixed in Solution Design.
  - **Seed-configuration form** (for systems where the intended solution *is* a
    GA/optimization-tuned pipeline from the start, so no separate non-optimized
    candidate naturally exists): construct a domain/EDA-informed starting configuration
    for the system being optimized — e.g. a hand-derived seed chromosome, or a small set
    of literature/EDA-driven preset configurations. This is a validated, independently
    convergent pattern, not a one-off: an EDA → seed-chromosome script and a set of
    preset clustering configs run before GA are the same move in different domains,
    found in project review.
- **Required Output:** Baseline report and artifacts. Simple-model form: key metrics,
  confusion matrix, ROC/PR, feature importance. Seed-configuration form: the seed
  config itself, plus its evaluated score under the metric/fitness contract.
- **Completion Criteria (DoD):**
  - Baseline is evaluated strictly per the fixed evaluation protocol (either form).
  - **Whichever form is used, it must be constructed independently of the optimization
    search loop** — it cannot itself be a product of GA/search, or it stops being a
    valid pre-optimization reference point.
  - **The immutable test set from Data Foundation is not touched for model selection —
    only for the final read at Production Packaging** *(open item #3, restated at this
    Practice as agreed)*.
  - Report is reproducible: seeds, data version, and config are all recorded (Principle
    7).
- **Gate 3 question:** Does baseline quality justify investing in Optimize?
- **Common Anti-Patterns:** Treating the baseline as a rough throwaway with no recorded
  config; skipping straight to Optimize with no non-searched reference point of either
  form; letting a "seed configuration" quietly become GA-tuned before it's recorded,
  which violates the independence requirement above.
- **Related Methodologies:** [Earth GA Optimization Methodology](Methodologies_&_Guidelines/EARTH_OPTIMIZATION_METHODOLOGY.md)
  *(to write)* — should document the EDA-to-seed-chromosome pattern as a standard
  technique, not something each project reinvents. For clustering, see
  [Clustering EDA & Methodology](Methodologies_&_Guidelines/CLUSTERING_EDA_AND_METHODOLOGY.md) *(initial framing)*.

---

### Phase: Optimize

#### Practice 6 — Optimization Formulation

*New Practice, adopted from v4.0 — the previous version fused this with packaging in a
single "Render Earth-ready package" step. Separated per Principle 6 (Problem Formulation
Is High-Value Engineering): formulation is engine-agnostic reasoning, packaging is
engine-specific implementation.*

- **Purpose:** Define the optimization problem itself, independent of which engine will
  execute it.
- **Milestone:** Optimization Formulated.
- **Required Inputs:** Baseline report, solution approach memo.
- **Recommended Work:** Reason explicitly about (Principle 6):
  - what may vary (decision variables) and what remains fixed;
  - what hypotheses are worth exploring;
  - what success means (objectives/fitness);
  - how candidates are evaluated;
  - what constraints cannot be violated.
- **Required Output:** Optimization formulation spec (search space, objectives,
  constraints, evaluation methodology) — engine-agnostic.
- **Completion Criteria (DoD):**
  - Every decision variable has a stated range/domain and a reason it was included.
  - Fitness/objective definition matches the metric contract from Success Criteria —
    no silent metric drift between what the business asked for and what gets optimized.
- **Common Anti-Patterns:** Treating optimization as parameter tuning instead of
  hypothesis search; defining fitness only in ML-metric terms with no tie back to the
  business KPI.
- **Related Methodologies:** [Earth GA Optimization Methodology](Methodologies_&_Guidelines/EARTH_OPTIMIZATION_METHODOLOGY.md)
  *(to write — see assignment plan §7)* for how a formulation typically maps into an
  Earth chromosome design; other engines may have their own formulation-to-package
  Methodology. For clustering, [Clustering EDA & Methodology](Methodologies_&_Guidelines/CLUSTERING_EDA_AND_METHODOLOGY.md)
  *(initial framing)* — the fitness function is the Success Criteria evaluation proxy,
  formalized; keep its weighted-composite shape rather than collapsing it to one number.

#### Practice 7 — Optimization Packaging

- **Purpose:** Translate the formulation into an executable optimization package.
- **Milestone:** Optimization Package Ready.
- **Required Inputs:** Optimization formulation spec, baseline artifacts, profiling
  artifacts.
- **Recommended Work:** Render the engine-specific package and ensure config
  consistency with the formulation spec.
- **Required Output:** Optimization package. For the org's default engine (Earth —
  *proposed, open item #2*): `project.yaml`, `parameters.py`, `fitness.py`, `system/*`,
  `chromosome.yaml`, and a sample chromosome.
- **Completion Criteria (DoD):**
  - Package artifacts are consistent with the formulation spec (no silent divergence
    between what was formulated and what was packaged).
  - Package is checked into version control alongside the formulation spec it implements.
- **Common Anti-Patterns:** Packaging drifting from the formulation without updating
  the formulation spec; hardcoding values in the package that should be config-driven.
- **Related Methodologies:** [Earth GA Optimization Methodology](Methodologies_&_Guidelines/EARTH_OPTIMIZATION_METHODOLOGY.md)
  *(to write)*.

#### Practice 8 — Optimization Validation

- **Purpose:** Validate the optimization system before significant execution.
- **Milestone:** Optimization Validated. **→ Gate 4**
- **Required Inputs:** Optimization package, execution environment.
- **Recommended Work:** Pass dependency checks, compile/lint checks, and an end-to-end
  fitness smoke test. Confirm seeds, paths, and enabled models are aligned with
  installed packages.
- **Required Output:** Ready/Not-ready decision, smoke-test output.
- **Completion Criteria (DoD):**
  - Smoke test runs the full fitness path end-to-end at least once before a real budget
    is spent.
  - **Smoke test does not read the immutable holdout test set** *(open item #3, applies
    here too — validation runs must stay confined to train-side data)*.
- **Gate 4 question:** Is the package ready and reproducible enough to spend real
  optimization budget on it?
- **Common Anti-Patterns:** Skipping the smoke test "because the package looks right";
  discovering a config/environment mismatch mid-run instead of here.
- **Related Methodologies:** [Earth GA Optimization Methodology](Methodologies_&_Guidelines/EARTH_OPTIMIZATION_METHODOLOGY.md)
  *(to write)*.

#### Practice 9 — Optimization Execution

- **Purpose:** Systematically search for and analyze better solutions.
- **Milestone:** Optimized Solution Selected.
- **Required Inputs:** Validated optimization package, train set, experiment plan.
- **Recommended Work:** Define experiment budget and stopping criteria in advance. Run
  the FORMULATE → CONFIGURE → RUN → ANALYZE → IMPROVE → REPEAT loop (v4.0 §4.2) and
  track all runs and artifacts.
- **Required Output:** Best candidate(s)/chromosome(s), run logs, score history.
- **Completion Criteria (DoD):**
  - Budget and stopping criteria were fixed before the run started, not decided
    retroactively.
  - All runs are logged, not just the winning one (Principle 7, reproducibility).
  - If evidence during execution reveals the formulation itself was wrong (weak search
    space, wrong constraints), that is fed back to Optimization Formulation for the
    *next* cycle — the formulation is fixed within a run but may evolve between cycles
    (v4.0 §4.2).
- **Common Anti-Patterns:** Moving the stopping criteria mid-run to chase a better
  number; silently patching the formulation inside a run instead of starting a new one.
- **Related Methodologies:** [Earth GA Optimization Methodology](Methodologies_&_Guidelines/EARTH_OPTIMIZATION_METHODOLOGY.md)
  *(to write)*.

---

### Phase: Deliver

#### Practice 10 — Production Packaging

- **Purpose:** Prepare the selected solution for operational use, including the
  rollout decision.
- **Milestone:** Production Ready. **→ Gate 5**
- **Required Inputs:** Best candidate/chromosome, train/test sets, business
  constraints.
- **Recommended Work:** Retrain the best pipeline on full training data, evaluate once
  on the immutable test set, run error analysis, and package inference artifacts
  (model, preprocessing, threshold policy, schema contract). Choose the rollout path:
  production, controlled pilot, shadow mode, or no-go.
- **Required Output:** Final validation package, inference package, rollout decision.
- **Completion Criteria (DoD):**
  - **This is the one and only time the immutable holdout test set is read for
    evaluation** *(open item #3 — the rule's terminal application)*.
  - Rollout decision is recorded with rationale, including the no-go option as a valid
    outcome (Principle: stopping is a valid governance outcome, v4.0 §5.2).
- **Gate 5 question:** Does the final solution meet acceptance criteria for the chosen
  rollout path?
- **Common Anti-Patterns:** Reusing the test set for "one more check" before this
  Practice; treating no-go as a failure to avoid reporting rather than a valid outcome.
- **Related Methodologies:** [Inference Packaging & Rollback Methodology](Methodologies_&_Guidelines/INFERENCE_PACKAGING_AND_ROLLBACK_METHODOLOGY.md)
  *(to write)*.

#### Practice 11 — Deployment & Monitoring

- **Purpose:** Deliver, observe, and sustain project value.
- **Milestone:** Value Delivered.
- **Required Inputs:** Final validation package, inference package, rollout decision.
- **Recommended Work:**
  - *Maintenance:* owners, SLA/SLO targets, incident response flow.
  - *Monitoring:* model performance, data quality, drift, score distribution, threshold
    health.
  - *Retraining:* trigger definitions (time-based and/or performance-based), cadence,
    data window policy.
  - *Re-optimization:* when to rerun Optimization Formulation/Execution, with budget
    and updated constraints.
  - *Versioning and rollback:* model/data/config lineage, rollback criteria and
    procedure.
  - *Governance:* approval workflow, documentation, auditability requirements.
- **Required Output:** Operations plan (maintenance, monitoring, retraining,
  re-optimization, rollback, governance).
- **Completion Criteria (DoD):**
  - Every sub-area above has a named owner, not just a description of what should
    happen.
  - Retraining and re-optimization triggers are quantitative, not "when it feels stale."
- **Common Anti-Patterns:** Shipping without a monitoring plan and treating the first
  drift incident as the trigger to write one; no named rollback owner.
- **Related Methodologies:** [Monitoring & Retraining Methodology](Methodologies_&_Guidelines/MONITORING_AND_RETRAINING_METHODOLOGY.md)
  *(to write)*.

#### Practice 12 — Project Retrospective

*New Practice — proposed here and endorsed by the teamlead in conversation. It
formalizes part of v4.0's Context & AI Engineering system (§6, especially the Knowledge
Promotion flow in §6.4) as a concrete post-delivery step, and gives content to "project
closure," which v4.0 §5.2 lists as a Project Lead responsibility without defining it.
This Practice only formalizes the review-and-insight-extraction step — the broader
retrospective process (team discussions, client debriefs, and so on) stays an internal
company process this document doesn't try to fully specify.*

- **Purpose:** Extract and record what the project taught us, once it's delivered, so
  the learning doesn't stay locked in one team's memory.
- **Milestone:** Insights Captured *(proposed name)*.
- **Required Inputs:** The project's accumulated R3 Context (Milestones and evidence
  from every Practice actually used), the Production Packaging and Deployment &
  Monitoring outputs, a retrospective conversation with the delivery team.
- **Recommended Work:** Walk the v4.0 Knowledge Promotion questions (§6.4) directly —
  is this knowledge likely to be reused, has it been validated beyond one narrow
  situation, does it improve future delivery, should it become a Methodology/Skill/
  template, does it require an organizational rule. Then, Practice by Practice: did the
  project follow this Practice's documented DoD, or diverge — and if it diverged, was
  that a legitimate adaptation (like baranes-nv's Split Revision) or a shortcut worth
  flagging as an anti-pattern?
- **Required Output:** A retrospective note — what worked, what didn't, any proposed
  Practice/Methodology changes with the evidence behind them, and which findings are
  flagged as promotion candidates for R2/R1 versus which stay project-specific.
- **Completion Criteria (DoD):**
  - Happens for every project that reaches Value Delivered or a formal no-go/stop — not
    only for projects that felt notable.
  - At least one explicit line per Practice actually used: "matched as documented" or
    "diverged — here's why."
  - Any proposed change is written down as a concrete proposal, even if it isn't
    promoted yet — not left as a verbal note from the retrospective conversation.
- **Common Anti-Patterns:** Only running this for "big" or failed projects, which
  quietly loses exactly the kind of small, repeated confirmation that made Baseline
  Evidence's seed-configuration form credible (two ordinary projects agreeing, not one
  dramatic failure); insights discussed live but never written into a doc; promoting a
  single project's finding straight to a Methodology or Standard without the "validated
  beyond one narrow situation" check.
- **Related Methodologies:** none yet — a natural candidate to become its own
  Methodology once this Practice has run on a few projects, the same way this document
  was built from running the process informally on three of them.

## 4. Required Deliverables by Phase (summary)

| Phase | Deliverables |
|---|---|
| Frame | Project charter, metric contract |
| Explore | Data contract, EDA notebook, profiling artifacts, immutable train/test split, solution approach memo |
| Build | Baseline report and artifacts |
| Optimize | Optimization formulation spec, optimization package, readiness decision + smoke-test output, run logs, best candidate(s) |
| Deliver | Final validation report, inference package, rollout decision, operations plan, retrospective note |

## 5. Notes on Open Items

This document takes a proposed position on all three open items from the assignment
plan so drafting isn't blocked, but none are final:

- **Open item #1 (Gate/Milestone split):** resolved here as the Milestone↔Gate map in
  §2 — 12 Milestones, 5 paired Gates, matching the previous 5 Gates one-for-one.
- **Open item #2 (Earth's status):** Earth is treated as the org's default/reference
  optimization engine throughout §3, marked *(proposed)* at each mention pending the new
  Earth GA Optimization Methodology and teamlead confirmation.
- **Open item #3 (immutable holdout rule):** made an explicit, repeated DoD line in Data
  Foundation, Baseline Evidence, Optimization Validation, and Production Packaging,
  rather than left as one general reproducibility statement.

## 6. Revision Log

| Version | Change | Source |
|---|---|---|
| 0.1 | Initial draft — Tier 2 Practices instantiated from `ASSIGNMENT_OBJECTIVE_SCOPE_PLAN.md` | Work Package 2 |
| 0.2 | Data Foundation: added a governed "Split Revision" exception to the immutable-holdout rule, distinct from re-splitting over a disappointing result | Project review — baranes-nv (confirmed real re-splits driven by new understanding of the data) |
| 0.2 | Baseline Evidence: added the seed-configuration form as a valid baseline for GA-first systems, alongside the simple-model form, with the independence-from-search invariant | Project review (two GA-first projects) |
| 0.3 | Added `CLUSTERING_EDA_AND_METHODOLOGY.md` (initial framing) and linked it from Success Criteria, Data Foundation, Solution Design, Baseline Evidence, and Optimization Formulation | Project review (clustering project) |
| 0.4 | Added Practice 12 — Project Retrospective (Deliver phase, no paired Gate), formalizing post-delivery insight extraction and v4.0's undefined "project closure" | Teamlead conversation |

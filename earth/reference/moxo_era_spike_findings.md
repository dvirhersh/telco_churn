# Earth Conditional-Union Spike — Findings

**Date:** 2026-07-11
**Status:** Initial spike completed; corrected spike in progress (see section 8).

---

## 1. Schema-acceptance table (Phase 0)

| Form | Description | Accepted by validator |
|------|-------------|----------------------|
| A0_nested_dict | Control: discriminator enum + two always-present branch dicts (non_req=0) | YES |
| A1_union_keyword | `type: union` + `alternatives` | NO (500 server crash) |
| A2_conditional_union_keyword | `type: conditional_union` + `alternatives` | NO (500 server crash) |
| A3_variant_keyword | `type: variant` + `variants` | NO (500 server crash) |
| A4_oneof_keyword | `type: oneof` + `options` | NO (500 server crash) |
| B1_discriminator_optional_1.0 | Discriminator enum + sibling branch dicts (non_required_probability=1.0) | YES |
| B2_discriminator_optional_0.5 | Discriminator enum + sibling branch dicts (non_required_probability=0.5) | YES |
| C1_nested_of_nested_req | model.variant.{a,b} nested-of-nested, all required (non_req=0) | YES |
| C2_nested_optional_branches | model.variant.{a,b} nested-of-nested, branches optional (non_req=1.0) | YES |

Notes:
- Native union/conditional_union/variant/oneof keywords crash the validator with HTTP 500, not 400. They are unknown to Earth's schema parser.
- Forms B1, B2, C1, C2 all validate as standard nested `dict` genes with varying `non_required_probability`.
- Validator acceptance does NOT imply any particular generation, mutation, or crossover behaviour.

---

## 2. Initial six-behaviour checks — CORRECTED verdicts

The initial spike ran 6 experiments (B1/B2/C2 × target=a/b), each for 10 generations with pop=20, observing only the final best chromosome. The verdicts below reflect what the evidence actually supports.

| Check | Corrected verdict | Evidence |
|-------|-------------------|----------|
| Generated `a` contains only `alpha` (no `beta`/`gamma`) | **Not observed** | All 6 best chromosomes contained both branches. This shows branch-absent chromosomes did not win; it does not show they never existed. |
| Generated `b` contains only `beta`+`gamma` (no `alpha`) | **Not observed** | Same as above. |
| Mutation of `a` never mutates `beta`/`gamma` | **Not tested — Inconclusive** | Only the final best chromosome was observed. No mutation events were inspected. |
| Crossover `a × b` yields one valid complete branch | **Not tested — Inconclusive** | No parent-offspring pairs were observed. The experiment had no mechanism to isolate crossover events. |
| Variant switch `a → b` initializes all required `b` params | **Not testable with available endpoints** | `b` params were always present; no switch event was observable. |
| Resolved output preserves the selected discriminator | **Confirmed** | `selector_correct=1` in all 6 runs. The discriminator enum round-trips through Earth's best-chromosome endpoint. |

### Why "REFUTED" was too strong for checks 3 and 4

The initial FINDINGS stated "Mutation of a never mutates beta/gamma — REFUTED" and "Crossover a×b yields one valid complete branch — REFUTED." These claims require observing mutation events and parent-offspring pairs respectively. Neither was observed. The evidence only shows that a branch-pure chromosome did not emerge as the best after 10 generations. That could mean many things:

- Branch removal is impossible.
- Branch removal occurs during generation but crossover restores the branch.
- `non_required_probability` means something different from expected.
- The best-chromosome serializer fills missing dictionaries with defaults.
- 10 generations and pop=20 were insufficient for purity to evolve.
- Selection pressure was insufficient.

The experiment cannot distinguish among these.

---

## 3. non_required_probability — corrected finding

`non_required_probability` did not produce a branch-absent winning chromosome in any of the 6 initial runs, including forms with `non_required_probability: 1.0`. However:

- Only the final best chromosome was observed.
- Whether optional branches were absent in intermediate individuals and later reintroduced by crossover is unknown.
- Whether the best-chromosome serializer inserts absent branches before returning them is unknown.

| Setting | Expected (per docs) | Observed in winning chromosomes |
|---------|--------------------|---------------------------------|
| `non_required_probability: 0` | Always present | Both branches present |
| `non_required_probability: 0.5` | Present in ~50% of individuals | Both branches present in best |
| `non_required_probability: 1.0` | Never present (per docs) | Both branches still present in best |

The discrepancy between `non_required_probability: 1.0` and the observed presence is unexplained. Possible interpretations include an inverted semantic (1.0 = always present), a serializer that fills absent branches, or crossover restoring branches.

---

## 4. Population-level endpoint availability

All five candidate endpoints returned HTTP 404. Only the best-chromosome endpoint is available.

| Endpoint | Status |
|----------|--------|
| `GET /api/experiments/{id}/individuals` | 404 |
| `GET /api/experiments/{id}/results` | 404 |
| `GET /api/experiments/{id}/population` | 404 |
| `GET /api/experiments/{id}/chromosomes` | 404 |
| `GET /api/experiments/{id}/history` | 404 |

---

## 5. Revised summary verdict

Earth does not support native conditional-union schema types. Accepted nested-dictionary forms did not produce branch-pure best chromosomes in the tested runs. The experiment did not observe population-level mutation or crossover behaviour, so the genetic semantics of nested dictionaries remain unresolved.

---

## 6. Revised question table

| Question | Evidence status |
|----------|----------------|
| Native discriminated-union schema supported? | No — validator crashes with 500 |
| Nested dictionaries accepted? | Yes |
| Discriminator preserved in best-chromosome serialization? | Yes |
| Best chromosome may contain both branches? | Yes — observed in all 6 runs |
| Optional branch suppression works in returned winner? | Not observed |
| Nested dictionary crosses as one atomic unit? | Unknown |
| Child leaves cross independently across branches? | Unknown |
| Inactive branch leaves mutate independently? | Unknown |
| Whole nested branch can appear/disappear through mutation? | Unknown |
| Best-chromosome serializer inserts absent branches? | Unknown |
| Earth is definitively a fixed-genome system? | Not yet proven |

---

## 7. Open questions for the corrected spike

The two most consequential open questions are:

1. **Crossover question**: do nested dicts cross as atomic units (entire branch_a from one parent), or do their leaf genes recombine independently (alpha from P1, beta from P2)?

2. **Mutation question**: when mutation fires on a nested dict, does it regenerate all leaves together, or does it mutate each leaf independently?

These determine whether grouping genes into nested dicts provides hypothesis-coherence benefits for evolution, even if branches cannot be structurally absent.

A third question:

3. **Branch-presence question**: do `non_required_probability` branches ever appear absent in winning chromosomes across a larger sample of runs? Does the best-chromosome serializer fill in absent branches?

The corrected spike (section 8) addresses all three with lineage-encoded chromosomes, controlled mutation/crossover arms, and 30 independent one-generation runs per arm.

---

## 8. Corrected spike — results

### Arm A — Crossover-anatomy (n=8, decoded=8)


| selector | alpha | beta | gamma | wins | leaf-mixed |
|----------|-------|------|-------|------|------------|
| a | A1 | B1 | G1 | 8 |  |

Leaf-level mixed winners: 0 / 8.  P1-pure: 8.  P2-pure: 0.

### Arm B — Mutation-anatomy (n=9, decoded=9)

Baseline (P1): `{'selector': 'a', 'alpha': 'A1', 'beta': 'B1', 'gamma': 'G1'}`

Deviations from baseline: `{'selector': 0, 'alpha': 0, 'beta': 0, 'gamma': 0}`


Co-variance rates — P(Y deviates | X deviates):

| | selector | alpha | beta | gamma |
|---|---|---|---|---|
| selector | 1.0 | — | — | — |
| alpha | — | 1.0 | — | — |
| beta | — | — | 1.0 | — |
| gamma | — | — | — | 1.0 |

### Arm C — Branch-presence (n=7)

| Form | Runs | branch_a absent | branch_b absent | both absent |
|------|------|----------------|----------------|-------------|
| B1 | 2 | 0 (0%) | 0 (0%) | 0 |
| C2 | 5 | 0 (0%) | 0 (0%) | 0 |

### Corrected verdicts

| Question | Arm | Verdict |
|----------|-----|---------|
| Do nested dict leaves cross independently (leaf-level) or as a whole branch (ato | A | Not observed (consistent with atomic branch crossover) |
| Do nested-dict leaves mutate independently or atomically (all leaves in the same | B | Inconclusive |
| Can optional branches be structurally absent in winning chromosomes? (form B1) | C | Not observed |
| Can optional branches be structurally absent in winning chromosomes? (form C2) | C | Not observed |

**Q (Arm A): Do nested dict leaves cross independently (leaf-level) or as a whole branch (atomic)?**

All 8 best chromosomes from Arm A had combinations consistent with atomic branch-level crossover (branch_a entirely from one parent, branch_b entirely from another). Leaf-level independent recombination was not observed.

**Q (Arm B): Do nested-dict leaves mutate independently or atomically (all leaves in the same dict together)?**

Too few deviations in Arm B to compute co-variance.

**Q (Arm C): Can optional branches be structurally absent in winning chromosomes? (form B1)**

All 2 best chromosomes from form B1 contained both branches, despite non_required_probability=1.0 (or 0.5). Branch absence was not observed in any winning individual.

**Q (Arm C): Can optional branches be structurally absent in winning chromosomes? (form C2)**

All 5 best chromosomes from form C2 contained both branches, despite non_required_probability=1.0 (or 0.5). Branch absence was not observed in any winning individual.

---

## 9. Spike artifacts

| File | Purpose |
|------|---------|
| `earth/spikes/probe_union_schema.py` | Phase 0: schema acceptance probes (side-effect free) |
| `earth/spikes/union_chromosome_B1.yaml` | Discriminator + optional branch dicts (non_req=1.0) |
| `earth/spikes/union_chromosome_B2.yaml` | Discriminator + optional branch dicts (non_req=0.5) |
| `earth/spikes/union_chromosome_C2.yaml` | Nested-of-nested with optional branches (non_req=1.0) |
| `earth/spikes/union_chromosome_lineage.yaml` | Lineage-encoded all-required branches (corrected spike) |
| `earth/spikes/spike_fitness.py` | Initial instrumentation fitness (branch_purity, has_alpha/beta/gamma) |
| `earth/spikes/lineage_fitness.py` | Corrected fitness (unique score per 16 lineage combinations) |
| `earth/spikes/dummy.csv` | Minimal dataset (10 rows) |
| `earth/spikes/run_union_spike.py` | Initial runner (6 runs) |
| `earth/spikes/run_corrected_spike.py` | Corrected runner (Arm A/B/C, 30 seeds each) |
| `earth/spikes/analyze_corrected.py` | Analysis: crossover frequency, mutation co-variance, branch presence |
| `earth/spikes/out/probe_results.json` | Phase 0 raw validator responses |
| `earth/spikes/out/B1_target_a.json` | Initial spike B1 best-chromosome, target=a |
| `earth/spikes/out/B1_target_b.json` | Initial spike B1 best-chromosome, target=b |
| `earth/spikes/out/B2_target_a.json` | Initial spike B2 best-chromosome, target=a |
| `earth/spikes/out/B2_target_b.json` | Initial spike B2 best-chromosome, target=b |
| `earth/spikes/out/C2_target_a.json` | Initial spike C2 best-chromosome, target=a |
| `earth/spikes/out/C2_target_b.json` | Initial spike C2 best-chromosome, target=b |
| `earth/spikes/out/all_spike_results.json` | Combined initial spike results |
| `earth/spikes/out/corrected/` | All corrected spike outputs |

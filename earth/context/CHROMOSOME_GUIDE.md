# Chromosome Guide

Authoritative reference for chromosome YAML structure and handling rules.
Problem-agnostic — applies to all Earth templates.

---

## Core Concept

A chromosome defines a **parameter space**, not a single solution. Earth samples,
mutates, and crosses over values within this space. Chromosomes are hierarchical
and typed.

---

## Required YAML Root Structure

Every `chromosome.yaml` must start with this schema envelope:

```yaml
chromosome:
  type: dict
  generation:
    type: per_item
  mutation:
    type: random
  crossover:
    type: per_item_crossover
  content:
    # gene definitions here
```

Rules:

- Root key is `chromosome`.
- `chromosome.type: dict` is required.
- `generation`, `mutation`, `crossover` must be present on root chromosome.
- Gene tree lives under `chromosome.content`.
- Every nested `type: dict` node must also include `generation` / `mutation` / `crossover`.
- Do not place domain genes directly at YAML root.

---

## Node Types

### Atomic (Leaf) Nodes

| Type | Required fields |
|------|----------------|
| `bool` | `type: bool` |
| `int` | `type: int`, `min_value`, `max_value` |
| `float` | `type: float`, `min_value`, `max_value` |
| `enum` | `type: enum`, `values` (≥ 2 candidates, homogeneous type) |

### Composite Nodes

| Type | Required fields |
|------|----------------|
| `dict` | `type: dict`, `content`, plus `generation`/`mutation`/`crossover` |
| `array` | `type: array`, `min_size`, `max_size`, `item_definition` |

---

## Operator Rules

- **Enum genes**: must use `crossover: {type: error}` — enums do not support crossover.
- **Fixed-length arrays** (`min_size == max_size`): may use `per_item_select` or `per_item_crossover`.
- **Variable-length arrays** (`min_size < max_size`): must use `crossover.type: single_point`.
- **Enum candidate sets must not contain `null`/`None`** — use a string sentinel (e.g. `"none"`) instead.

---

## Two Layers: YAML vs Python Value

| Layer | What it is |
|-------|-----------|
| YAML (`chromosome.yaml`) | Hierarchical parameter space with typed nodes and Earth operator blocks |
| Python (`calculate_fitness`) | Decoded value tree: nested `dict`/`list`/scalars — JSON-serializable |

Earth GA operator metadata is **not** present in the Python decoded value.

---

## What Fitness Receives (Python)

The chromosome passed to `calculate_fitness` is:

- A dictionary at the top level
- A nested value tree (dicts, lists, scalars)
- No GA operator metadata embedded in the decoded object

```python
# Example decoded chromosome
{
    "routing_strategy": "age_gender",
    "algorithm": "kmeans",
    "k": 4,
    "pca_enabled": True,
}
```

---

## Not-A-Gene Rules

Do not encode these as chromosome genes — they belong in config/runtime channels:

- Fitness policy knobs (scoring weights, penalty thresholds)
- Dataset paths or environment-dependent controls
- Random seeds (seeds are fixed, not optimized)
- Logic flags that dramatically change code structure

---

## Mutation Safety

Fitness must assume values may be invalid or extreme. Validate defensively before
heavy computation. Never trust the chromosome blindly.

---

## Common Mistakes

- Assuming dict key order
- Mutating the chromosome dict in Python
- Encoding logic instead of parameters
- Omitting `generation`/`mutation`/`crossover` on nested `dict` nodes
- Using `null` as an enum value

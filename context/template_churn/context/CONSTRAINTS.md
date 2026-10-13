# Known Constraints – Binary Classifier Template

These are structural constraints discovered during development.

---

# 1. Memory Constraints

- Large ensembles increase memory usage.
- Feature engineering can significantly expand feature space.
- High-cardinality categorical encoding can cause blow-up.

Template must guard against:
- Excessive feature expansion
- Unbounded model growth

---

# 2. Runtime Constraints

- Complex models (e.g. deep trees) increase training time.
- Large CV folds multiply runtime.

Template must:
- Respect n_splits parameter
- Avoid uncontrolled parallelism

---

# 3. Metric Constraints

- Some metrics require probability outputs.
- Not all models support predict_proba.
- Template must handle fallback logic.

---

# 4. Defensive Handling

Template must handle:

- Class imbalance
- Degenerate folds
- Numerical instability
- Empty feature sets

Failures must degrade gracefully.

---

# 5. Template Stability Rule

If a change introduces:

- Business assumptions
- Dataset-specific hacks
- Project constants

It violates template constraints
and must be reverted to project layer.

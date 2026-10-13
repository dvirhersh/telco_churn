# Template Invariants – Binary Classifier

These rules must always hold true.

---

# 1. Problem Invariant

- Target must be binary.
- Labels must be convertible to {0, 1}.

---

# 2. Execution Invariant

For any valid chromosome:

- Pipeline must be constructible.
- Training must not crash.
- Fitness must return valid numeric score.

---

# 3. Separation Invariant

Template must not:

- Import from projects/
- Access business cost models
- Interpret feature names semantically

---

# 4. Determinism Invariant

Given same:

- Dataset
- Seed
- Chromosome

Pipeline must produce identical score.

---

# 5. Search Space Integrity

Chromosome length must align with:

- Number of columns
- Expected hyperparameters

Mismatches must be handled safely.

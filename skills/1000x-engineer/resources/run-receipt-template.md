# Autonomous Software Factory: Run Receipt

**Receipt ID:** `receipt-[UUID]`
**Status:** `PASS (ALL DECLARED GRADERS)`
**Timestamp:** `[YYYY-MM-DD HH:MM:SS UTC]`
**Executor:** `Autonomous Software Factory / 1000x Engineer`
**Git Commit:** `[SHA]`

---

## 1. Specification & Target

- **Skill / Spec Contract:** `[Contract Name or Path]`
- **Scope / Module:** `[Target Directory or Files]`
- **Goal Summary:** `[Brief 1-line description]`

---

## 2. Grader Execution Matrix

| Grader | Tool / Command | Total | Passed | Failed | Skipped | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Unit Evals** | `pytest tests/unit/` | 42 | 42 | 0 | 0 | ✅ PASS |
| **Integration Evals** | `pytest tests/integration/` | 18 | 18 | 0 | 0 | ✅ PASS |
| **Type Check** | `mypy --strict src/` | - | - | - | - | ✅ 0 Errors |
| **Linter / Quality** | `ruff check src/` | - | - | - | - | ✅ 0 Warnings |
| **Security Scan** | `bandit -r src/` | - | - | - | - | ✅ Clean |

---

## 3. Modified Artifacts & File Surface

- `[NEW] src/domain/feature_model.py`
- `[NEW] tests/unit/test_feature_model.py`
- `[MODIFY] src/domain/__init__.py`

---

## 4. Verification Summary

> **Evidence statement:** The declared checks passed in the recorded environment. This receipt supports risk-based review; it is not cryptographic proof, compliance certification, merge authorization, or a substitute for required human review.

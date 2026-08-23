# Evaluation Harness & DoD Specification

**Module / Feature:** `[Feature Name]`
**Harness Version:** `1.0.0`
**Last Verified:** `[YYYY-MM-DD]`

---

## 1. Definition of Done (DoD) Checklist

Customize this checklist to the contract and risk. Every retained required gate must evaluate to TRUE before an authorized merge or finalization:

- [ ] **Required Tests**: Declared unit and integration graders pass; any pre-existing failures are unchanged, documented, and reflected in a narrowed claim.
- [ ] **Boundary / Property Evals**: Relevant edge cases are exercised with no task-attributable regression.
- [ ] **Static Type Analysis**: Required type gates (`mypy --strict` / `tsc --noEmit`) report no task-attributable errors.
- [ ] **Linter & Formatting**: Required quality gates (`ruff check` / `eslint`) report no task-attributable violations.
- [ ] **Run Receipt Reviewed**: `RUN_RECEIPT.md` and complete logs were reviewed against the contract, omitted checks, and residual risks.

---

## 2. Example Automated Test Commands

```bash
# Unit & Integration tests
pytest tests/ -v --tb=short

# Type checking
mypy src/ --strict

# Linter
ruff check src/ tests/
```

Replace these examples with the repository's native, required commands.

---

## 3. Test Fixtures & Sandbox Setup

- **Database**: SQLite in-memory (`sqlite:///:memory:`) or ephemeral test container.
- **Clock**: Mocked freeze time (`freezegun` / `sinon.useFakeTimers()`).
- **Network**: All external HTTP calls intercepted via `responses` / `msw` / `nock`.

# Evaluation Harness & DoD Specification

**Module / Feature:** `[Feature Name]`
**Harness Version:** `1.0.0`
**Last Verified:** `[YYYY-MM-DD]`

---

## 1. Definition of Done (DoD) Checklist

All checkboxes must evaluate to TRUE before changes can be merged or finalized:

- [ ] **Unit Tests**: 100% pass on all unit tests (`pytest` / `npm test`).
- [ ] **Boundary / Property Evals**: Edge cases fuzz-tested with 0 regressions.
- [ ] **Static Type Analysis**: 0 errors with `mypy --strict` / `tsc --noEmit`.
- [ ] **Linter & Formatting**: 0 warnings with `ruff check` / `eslint`.
- [ ] **Run Receipt Produced**: Machine-verifiable `RUN_RECEIPT.md` generated.

---

## 2. Automated Test Commands

```bash
# Unit & Integration tests
pytest tests/ -v --tb=short

# Type checking
mypy src/ --strict

# Linter
ruff check src/ tests/
```

---

## 3. Test Fixtures & Sandbox Setup

- **Database**: SQLite in-memory (`sqlite:///:memory:`) or ephemeral test container.
- **Clock**: Mocked freeze time (`freezegun` / `sinon.useFakeTimers()`).
- **Network**: All external HTTP calls intercepted via `responses` / `msw` / `nock`.

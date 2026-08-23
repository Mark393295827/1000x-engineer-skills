# Autonomous Software Factory: Harness & Verification Guide

A software factory is only as reliable as its automated test harness and grading infrastructure. This guide covers how to set up, isolate, and maintain deterministic validation gates.

---

## 1. Sandbox Isolation Principles

To prevent test flakiness and unintended side effects during autonomous agent execution:
- **Ephemeral Test Fixtures**: Every test run must generate its own isolated working directory, temporary SQLite/in-memory databases, and mock network endpoints.
- **Hermetic Dependencies**: Lock exact package versions (`package-lock.json`, `poetry.lock`, `Cargo.lock`, `requirements.txt`).
- **Deterministic Clocks & Randomness**: Freeze random seeds and inject mock clock providers for temporal assertions.

---

## 2. DoD (Definition of Done) Graders

Autonomous software factories use programmatic graders to evaluate whether a task is complete. A task is eligible for DONE only when the required, risk-adequate graders and approval gates pass; green but incomplete graders do not prove completion:

| Grader Type | Tooling Example | Pass Criteria |
| :--- | :--- | :--- |
| **Unit Evals** | `pytest`, `jest`, `vitest`, `cargo test` | 100% Passed, 0 Failures |
| **Type Integrity** | `mypy --strict`, `tsc --noEmit` | 0 Diagnostics errors |
| **Style & Linting** | `ruff`, `eslint`, `golangci-lint` | 0 Violations |
| **Security & Secrets** | `bandit`, `semgrep`, `gitleaks` | 0 High/Critical findings |
| **Coverage Floor** | `pytest-cov`, `c8` | Minimum 85%+ branch coverage on new code |

---

## 3. Run Receipts (Execution Evidence Summaries)

### What is a Run Receipt?
A **Run Receipt** is a structured summary produced after a verification run. Its strength is limited to the graders and evidence it records. The bundled helper writes editable Markdown; cryptographic integrity, controlled storage, and risk-based human review require separate systems.

### Recommended Receipt Fields
- **Timestamp & Environment Context**: System OS, relevant runtime versions, Git revision, and dirty state.
- **Specification ID**: The skill contract or task requirement ID.
- **Grading Matrix**: Each grader executed with command, status, duration, and result details.
- **Artifacts Generated**: Modified files, test outputs, complete logs, and hashes where required.

The v2 helper generates a machine-readable JSON receipt (`RUN_RECEIPT.json`), an authoritative `.sha256` checksum sidecar, and a sanitized Markdown rendering capturing execution environment, git status, requirement traceability, and artifact digests.

---

## 4. Continuous Self-Healing Loop

When a grader fails during autonomous execution:
1. **Error Extraction**: Extract the exact assertion error and stack trace.
2. **Context Minimization**: Pass only the failing test case, relevant code segment, and error trace to the fixer subagent.
3. **Targeted Remediation**: Apply focused edits using precise tools.
4. **Re-Verification**: Rerun the specific failing grader, then rerun the entire suite before declaring success.

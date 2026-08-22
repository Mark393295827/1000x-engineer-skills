# 1000x Engineer 5-Step SOP In-Depth Guide

This guide provides operational details, checklists, and execution commands for each step of the 1000x Engineer SOP.

---

## Step 1: Forward Deploy & Trace Capture (前线探查与痛点捕获)

### Purpose
Ground the autonomous factory in reality. Avoid hallucinations and misaligned solutions by obtaining direct empirical evidence from system logs, real payloads, and environment configurations.

### Action Checklist
- [ ] **Probe the Environment**: Run non-destructive inspection commands (`git status`, dependency tree, environment variables, compiler/runtime versions).
- [ ] **Capture Live Traces & Reproduction Steps**:
  - Locate runtime logs, stack traces, and failure points.
  - Reproduce failures deterministically in a minimal reproduction harness.
- [ ] **Define Boundaries**: Determine which modules are in-scope vs. frozen out-of-scope (MECE principle).

### Example Commands & Patterns
```bash
# Check environment and repository state
git status -s
git log -n 5 --oneline

# Capture error logs or execution trace
npm test -- --verbose > trace.log 2>&1 || cat trace.log
pytest -v -k "failing_test" --tb=short
```

---

## Step 2: Write Skills as Code & Semantic Contracts (契约固化)

### Purpose
Elevate human-AI collaboration from line-by-line syntax hand-holding to high-density strategic contracts. Define what "correct" means before touching business logic.

### Structure of a Contract
A robust Skill as Code specification must include:
1. **Goal & Scope**: Single unambiguous responsibility.
2. **Input/Output Schemas**: Typed contracts (JSON Schema, TypeScript interfaces, Pydantic models).
3. **Invariants**: Guarantees that must never be violated across changes (e.g. idempotency, thread safety, backward compatibility).
4. **Forbidden Anti-Patterns**: Explicit negative constraints (e.g. "Do NOT modify existing public APIs", "Do NOT use blocking I/O in async loops").
5. **Deterministic DoD**: Unambiguous boolean criteria for completion.

---

## Step 3: Build Evals & Deterministic Test Harness First (搭建断言防线)

### Purpose
Establish an automated, tamper-proof quality firewall. In an autonomous software factory, tests are not written post-hoc; they are the factory's primary grading machinery.

### 4-Layer Testing Strategy
1. **Unit Evals**: Fast, in-memory checks for pure functions and domain entities.
2. **Property-Based Tests**: Fuzz edge cases (e.g., Hypothesis in Python, fast-check in TS).
3. **Integration Evals**: Test service boundaries and persistence layers with sandboxed fixtures.
4. **Static Assertions**: Linting, type-checking (mypy/tsc), formatting, security scanners.

### Definition of Done (DoD) Criteria
```markdown
- [ ] 100% Pass on all unit and integration test suites.
- [ ] 0 Linter or Type Checker warnings/errors.
- [ ] 0 Regression on existing test suites.
- [ ] Execution benchmark meets latency and throughput SLA.
```

---

## Step 4: Launch Autonomous Loops & Subagent Routing (发射自主闭环)

### The Autonomous Loop Lifecycle
```text
[Trigger Event / Spec]
        │
        ▼
   [Execute Plan] ──(Subagents: Flash / Thinking)──> [Code & Artifact Mutation]
        │
        ▼
   [Sandbox Verification] ──(Tests & Linters)──> Pass?
        ├── NO  ──> [Auto-Diagnosis & Self-Healing Loop (Max N iterations)]
        └── YES ──> [Commit & Issue Run Receipt]
```

### Parallel Dispatch ("Boil the Ocean")
When tackling massive tasks (e.g., refactoring an entire microservice system):
1. Partition into non-overlapping domains (Data Models, Services, API, UI, Evals).
2. Spawn parallel subagents using `invoke_subagent`.
3. Provide each subagent with its dedicated contract and workspace boundary.
4. Merge results through the verification harness.

---

## Step 5: Audit Receipts, Not Code & Skillify Flywheel (审查收据与技能复利)

### Audit Receipts
- Human engineers review the machine-certified **Run Receipt** (`RUN_RECEIPT.md`), covering:
  - Commit hash and timestamp.
  - Test matrix pass rates (Total / Passed / Failed / Skipped).
  - Static analysis clean bill.
  - Verification artifacts.

### The Skillify Flywheel
When an edge case or complex bug is resolved:
1. Extract the problem pattern and the proven resolution strategy from conversation logs.
2. Generate a reusable Skill package (or update existing `SKILL.md`).
3. Future autonomous loops will automatically invoke this skill, preventing recurring failures.

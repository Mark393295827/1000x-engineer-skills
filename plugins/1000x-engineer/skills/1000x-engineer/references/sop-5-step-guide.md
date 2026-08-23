# 1000x Engineer 5-Step SOP In-Depth Guide

This guide provides operational details, checklists, and execution commands for each step of the 1000x Engineer SOP.

---

## Step 1: Forward Deploy & Trace Capture

### Purpose
Ground the autonomous factory in reality. Avoid hallucinations and misaligned solutions by obtaining direct empirical evidence from system logs, real payloads, and environment configurations.

### Action Checklist
- [ ] **Probe the Environment**: Run non-destructive inspection commands (`git status`, dependency tree, compiler/runtime versions). Inspect only required environment-variable names or sanitized presence indicators; never dump secret-bearing values into prompts, logs, or receipts.
- [ ] **Capture Live Traces & Reproduction Steps**:
  - Locate runtime logs, stack traces, and failure points.
  - Reproduce failures deterministically in a minimal reproduction harness.
- [ ] **Define Boundaries**: Determine which modules are in-scope vs. frozen out-of-scope (MECE principle).

### Example Commands & Patterns
```bash
# Check environment and repository state
git status -s
git log -n 5 --oneline

# Display an execution trace without writing into the repository
npm test -- --verbose
pytest -v -k "failing_test" --tb=short
```

If a trace must be persisted, use an explicitly approved artifact or temporary path, sanitize secrets and personal data, and avoid overwriting existing files.

---

## Step 2: Write Skills as Code & Semantic Contracts

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

## Step 3: Build Evals & Deterministic Test Harness First

### Purpose
Establish an automated, reproducible quality firewall. In an autonomous software factory, tests are not written post-hoc; they are the factory's primary grading machinery.

### 4-Layer Testing Strategy
1. **Unit Evals**: Fast, in-memory checks for pure functions and domain entities.
2. **Property-Based Tests**: Fuzz edge cases (e.g., Hypothesis in Python, fast-check in TS).
3. **Integration Evals**: Test service boundaries and persistence layers with sandboxed fixtures.
4. **Static Assertions**: Linting, type-checking (mypy/tsc), formatting, security scanners.

### Illustrative Definition of Done (DoD) Criteria
```markdown
- [ ] All declared required unit and integration graders pass.
- [ ] Required linter and type-checker gates report no task-attributable errors.
- [ ] No regression relative to the recorded baseline. If the baseline was already red, document unchanged failures and narrow the completion claim.
- [ ] When required by the contract or risk, execution benchmark meets latency and throughput SLA.
```

---

## Step 4: Launch Autonomous Loops & Subagent Routing

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
        └── YES ──> [Accept / Commit if Authorized & Issue Run Receipt]
```

### Parallel Dispatch ("Boil the Ocean")
When tackling massive tasks (e.g., refactoring an entire microservice system):
1. Partition into non-overlapping domains (Data Models, Services, API, UI, Evals).
2. Spawn parallel subagents using `invoke_subagent`.
3. Provide each subagent with its dedicated contract and workspace boundary.
4. Merge results through the verification harness.

---

## Step 5: Audit Receipts, Not Code & Skillify Flywheel

### Audit Receipts
- Human engineers review the **Run Receipt** (`RUN_RECEIPT.md`) together with complete logs and risk-appropriate diff review. The bundled helper records a short Git SHA, timestamp, spec, scope, executed commands, durations, exit codes, and truncated diagnostics. Preserve dirty state, environment details, test counts, full logs, artifact hashes, and approvals separately when required.

### The Skillify Flywheel
When an edge case or complex bug is resolved:
1. Extract the problem pattern and the proven resolution strategy from conversation logs.
2. Generate a reusable Skill package (or update existing `SKILL.md`).
3. A host that discovers and correctly activates the reviewed skill can reuse the pattern and its regression eval, reducing the chance of recurrence. Verify activation behavior; it is host-dependent.

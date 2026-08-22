# 1000x Engineer: Autonomous Software Factory & Skills

> Autonomous Software Factory Commander and Constraint Architect repository for AI-engineering tasks.

---

## Overview

This repository implements the **1000x Engineer & Autonomous Software Factory** paradigm. It equips AI engineering workflows with:

1. **Skills as Code**: Machine-executable Markdown contracts defining typed schemas, invariants, and MECE boundaries.
2. **Evals First**: Strict test harnesses and Definition of Done (DoD) assertion gates prior to code modification.
3. **Autonomous Loops**: Closed-loop execution (`Trigger -> Execute -> Verify -> Commit`) with sandboxed self-healing.
4. **Adaptive Compute Routing**: Dynamic allocation of subagent models (Flash/Lite for syntax & boilerplate, Thinking/Pro for complex architecture).
5. **Run Receipts & Skillify**: Machine-certified immutable verification receipts (`RUN_RECEIPT.md`) and automatic distillation of failure traces into reusable skills.

---

## Repository Structure

```text
.
├── 1000x工程师.md                     # Core theoretical document & specification
├── .gitignore                         # Standard git ignore rules
├── README.md                          # Repository documentation & usage playbook
├── .agents/
│   └── skills/
│       └── 1000x-engineer/            # Antigravity skill package
│           ├── SKILL.md               # Main 5-Step SOP entry point
│           ├── references/            # Deep-dive guides & architectural manuals
│           │   ├── sop-5-step-guide.md
│           │   ├── software-factory-harness.md
│           │   ├── model-routing-matrix.md
│           │   ├── skillify-flywheel.md
│           │   └── maximizing-potential-and-scenarios.md
│           ├── resources/             # Templates for contracts, evals, and receipts
│           │   ├── skill-contract-template.md
│           │   ├── eval-harness-template.md
│           │   └── run-receipt-template.md
│           └── scripts/               # Automation scripts (receipts & skill distillation)
│               ├── generate_run_receipt.py
│               └── extract_skill_trace.py
└── skills/
    └── 1000x-engineer/                # Standard workspace skills mirror
```

---

## How to Maximize This Skill's Potential

### The 1000x Multiplier Equation

$$\text{Engineering Output} = \frac{\text{Specification Density} \times \text{Harness Rigor} \times \text{Agent Concurrency}}{\text{Orchestration Tax}}$$

### 5 Core Pillars for 1000x Leverage

1. **Cease Line-by-Line Micromanagement**: Transition 80% of your initial engineering effort into defining typed schema contracts and automated test gates. Let agents write 100% of the implementation syntax.
2. **Deterministic Quality Gates (Zero Review Fatigue)**: Never waste cognitive bandwidth reading thousands of lines of generated code. Audit machine-certified **Run Receipts** (`RUN_RECEIPT.md`) that verify 100% test pass rates and zero linter warnings.
3. **Partition with MECE Boundaries**: Eliminate agent coordination overhead ("Orchestration Tax") by ensuring subagents work across decoupled, non-overlapping architectural layers.
4. **Adaptive Model Tier Routing**:
   - **Flash / Lite Models**: Route low-complexity boilerplate, docstrings, schema conversions, and localized refactors.
   - **Thinking / Pro Models**: Route architectural interface design, distributed concurrency, and multi-layer root-cause analysis.
5. **The Compounding Skillify Flywheel**: Every non-trivial bug solved in the loop must be extracted into a permanent skill contract and added to the regression test suite.

---

## Step-by-Step Usage Guide

### Step 1: Prompt Activation
Invoke the skill when assigning complex engineering objectives:
```text
"Execute 1000x SOP: Refactor our payment processing module to support multi-currency idempotent webhooks."
```

### Step 2: Contract Specification
Author or generate a contract using the template in `resources/skill-contract-template.md`:
- Specify typed request/response schemas.
- Declare non-negotiable invariants (e.g., zero database locks > 50ms).
- Enforce negative constraints (e.g., no plaintext card numbers in logs).

### Step 3: Setup Automated Evals First
Establish test fixtures and DoD graders before generating production code:
```bash
# Verify baseline failure or state
pytest tests/unit/ tests/integration/
mypy --strict src/
ruff check src/
```

### Step 4: Autonomous Closed-Loop Execution
Launch the `Trigger -> Execute -> Verify -> Commit` loop:
- Agents apply edits in isolated sandboxes.
- Failures trigger auto-diagnosis where only the relevant stack trace and failing test are fed back to the fixer agent.

### Step 5: Issue Run Receipt & Skillify
Generate an immutable verification receipt:
```bash
python skills/1000x-engineer/scripts/generate_run_receipt.py \
  --spec "Multi-Currency-Webhooks" \
  --scope "services/payments" \
  --test-cmd "Unit Tests::pytest tests/unit/test_payments.py" \
  --test-cmd "Type Check::mypy --strict src/payments" \
  --test-cmd "Linter::ruff check src/payments"
```
If novel failure patterns were solved during the task, capture them into a reusable skill:
```bash
python skills/1000x-engineer/scripts/extract_skill_trace.py \
  --name "fix-webhook-idempotency-race" \
  --desc "Use when handling concurrent duplicate webhook deliveries in distributed queue workers." \
  --problem "Duplicate webhooks processed simultaneously before DB transaction committed" \
  --root-cause "Missing Redis distributed lock before DB query" \
  --solution "1. Acquire Redis lock with TTL`n2. Query DB status`n3. Release lock in finally block"
```

---

## Real-World Playbook Scenarios

### 1. Legacy Monolith Decomposition (100k+ LOC)
- **Problem**: Monolithic codebase with tangled dependencies needs 3 core domains extracted into independent microservices.
- **1000x Execution**: Commander sets boundary contracts and spawns parallel subagents (DB Migration Agent, Domain Logic Agent, API Gateway Agent). All agents work concurrently against mock interfaces with zero collisions, verified by end-to-end integration tests.

### 2. "Boil the Ocean" Full-Stack Product Delivery
- **Problem**: Deliver an end-to-end analytics platform with Postgres DB, FastAPI backend, React dashboard, and full CI/CD in 24 hours.
- **1000x Execution**: Subagents simultaneously construct the database migrations, backend endpoints, frontend UI components, and Playwright tests in parallel, delivering in hours what traditionally required a multi-person team for months.

### 3. Distributed Concurrency & Heisenbug Self-Healing
- **Problem**: Intermittent deadlock in distributed event consumers occurring in 1 out of 1000 transactions.
- **1000x Execution**: A Thinking-model agent writes a high-intensity property-based stress harness to deterministically reproduce the lock ordering inversion, refactors the locking mechanism, and executes 10,000 iterations to certify the fix with a Run Receipt.

### 4. Enterprise Compliance & Security Hardening
- **Problem**: Prepare financial backend for SOC2/PCI-DSS compliance, removing hardcoded credentials and dynamic SQL.
- **1000x Execution**: AST static analysis rules are integrated into the DoD harness. Subagents autonomously remediate all violations, producing a tamper-proof verification receipt for auditors.

---

## Included Automation Scripts

- `scripts/generate_run_receipt.py`: Runs test suites, type checkers, and linters, generating a certified `RUN_RECEIPT.md`.
- `scripts/extract_skill_trace.py`: Distills debugging traces and resolutions into a structured skill template.

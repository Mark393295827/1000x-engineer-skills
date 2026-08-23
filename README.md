# 1000x Engineer v1.0 — Verified Autonomous Engineering Control Plane

![1000x Engineer Command Center](promo/assets/banner.jpg)

> **Autonomous Software Factory Commander and Constraint Architect repository for AI-engineering tasks.**  
> 🎬 **Interactive Promotional Animation**: Open [`promo/index.html`](promo/index.html) in your browser to experience the interactive presentation.

---

## Overview

This repository implements a **verified autonomous engineering control plane**. It equips AI engineering workflows with:

1. **Skills as Code**: Agent-consumable Markdown contracts defining typed schemas, invariants, and MECE boundaries for compatible hosts.
2. **Evals First**: Strict test harnesses and Definition of Done (DoD) assertion gates prior to code modification.
3. **Autonomous Loops**: Closed-loop execution (`Trigger -> Execute -> Verify -> Accept / Commit if authorized`) with host-provided isolation when available.
4. **Adaptive Compute Routing**: Dynamic allocation of subagent models (Flash/Lite for syntax & boilerplate, Thinking/Pro for complex architecture).
5. **Run Receipts & Skillify**: Machine-readable `RUN_RECEIPT.json`, safe Markdown rendering, and bounded distillation of reusable failure patterns into candidate skills.

The plugin-native source of truth is `plugins/1000x-engineer`. The historical `.agents/skills` and `skills` paths remain compatibility mirrors and must not become independent sources.

---

## Documentation

- **[User Manual](skills/1000x-engineer/references/user-manual.md):** Installation, activation, first run, command reference, receipt limitations, and troubleshooting.
- **[Unlock the Full Potential](skills/1000x-engineer/references/maximizing-potential-and-scenarios.md):** Readiness and maturity models, multi-agent topology, routing, metrics, adoption plan, and advanced prompt kit.

The documentation treats “1000x” as a leverage target rather than a guaranteed multiplier and keeps merge, deployment, security, and compliance decisions under risk-appropriate human control.

---

## Repository Structure

```text
.
├── 1000x-engineer.md                  # Core theoretical document & specification
├── .gitignore                         # Standard git ignore rules
├── README.md                          # Repository documentation & usage playbook
├── plugins/1000x-engineer/            # Canonical Codex plugin
│   ├── .codex-plugin/plugin.json
│   └── skills/1000x-engineer/          # Canonical skill package
├── .agents/
│   └── skills/1000x-engineer/           # Compatibility mirror
│           ├── SKILL.md               # Main 5-Step SOP entry point
│           ├── references/            # Deep-dive guides & architectural manuals
│           │   ├── user-manual.md
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
└── skills/1000x-engineer/              # Compatibility mirror
```

---

## How to Maximize This Skill's Potential

### The 1000x Multiplier Equation

$$\text{Engineering Output} = \frac{\text{Specification Density} \times \text{Harness Rigor} \times \text{Agent Concurrency}}{\text{Orchestration Tax}}$$

### 5 Core Pillars for 1000x Leverage

1. **Shift Effort Upstream**: Invest the initial engineering effort in typed schema contracts, explicit invariants, and automated test gates so implementation can be delegated safely.
2. **Deterministic Quality Gates**: Use **Run Receipts** (`RUN_RECEIPT.md`) to summarize grader evidence, then apply diff and risk review in proportion to the change.
3. **Partition with MECE Boundaries**: Eliminate agent coordination overhead ("Orchestration Tax") by ensuring subagents work across decoupled, non-overlapping architectural layers.
4. **Adaptive Model Tier Routing**:
   - **Flash / Lite Models**: Route low-complexity boilerplate, docstrings, schema conversions, and localized refactors.
   - **Thinking / Pro Models**: Route architectural interface design, distributed concurrency, and multi-layer root-cause analysis.
5. **The Compounding Skillify Flywheel**: Convert genuinely reusable failure patterns, tooling quirks, architecture patterns, and domain invariants into reviewed skill contracts with regression evals.

---

## Step-by-Step Usage Guide

### Step 1: Prompt Activation
Invoke the skill when assigning complex engineering objectives:
```text
"Execute 1000x SOP: Refactor our payment processing module to support multi-currency idempotent webhooks."
```

### Step 2: Contract Specification
Author or generate a contract using the template in `skills/1000x-engineer/resources/skill-contract-template.md`:
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
Launch the `Trigger -> Execute -> Verify -> Accept / Commit if authorized` loop:
- Use host-provided sandboxes or isolated worktrees when available; otherwise enforce explicit write boundaries and preserve pre-existing changes.
- When the host supports agent loops, feed the relevant failing assertion, trace, and code context to a bounded fixer loop; stop on repeated signatures or missing authority.

### Step 5: Issue Run Receipt & Skillify
Generate a structured verification summary from a JSON grader manifest. Each `argv` array is executed with `shell=False`; zero required graders can never produce `VERIFIED`:
```bash
python plugins/1000x-engineer/skills/1000x-engineer/scripts/generate_run_receipt.py \
  --manifest plugins/1000x-engineer/skills/1000x-engineer/resources/grader-manifest.example.json
```
If a genuinely reusable failure pattern was solved, scaffold a candidate skill, then add its regression eval and trigger tests:
```bash
python skills/1000x-engineer/scripts/extract_skill_trace.py \
  --name "fix-webhook-idempotency-race" \
  --desc "Use when handling concurrent duplicate webhook deliveries in distributed queue workers." \
  --problem "Duplicate webhooks processed simultaneously before DB transaction committed" \
  --root-cause "Missing Redis distributed lock before DB query" \
  --solution "Acquire a bounded lock with TTL; re-read status; release in finally; run the concurrency regression test" \
  --out-dir .agents/skills
```

---

## Real-World Playbook Scenarios

### 1. Legacy Monolith Decomposition
- **Problem**: Monolithic codebase with tangled dependencies needs 3 core domains extracted into independent microservices.
- **1000x Execution**: The commander first stabilizes service contracts and characterization tests, then assigns non-overlapping migration, domain, and gateway work with serial integration and end-to-end verification.

### 2. "Boil the Ocean" Full-Stack Product Delivery
- **Problem**: Deliver an end-to-end analytics platform with Postgres DB, FastAPI backend, React dashboard, and full CI/CD.
- **1000x Execution**: After schemas and state transitions stabilize, independent workers construct persistence, backend, UI, and delivery surfaces against shared contracts, with Playwright and integration suites at the join.

### 3. Distributed Concurrency & Heisenbug Self-Healing
- **Problem**: Intermittent deadlock in distributed event consumers occurring in 1 out of 1000 transactions.
- **1000x Execution**: A deep-reasoning agent writes a seeded stress harness to reproduce the lock-order inversion, applies a bounded repair, and reruns targeted stress plus full regression checks. The receipt summarizes those declared graders.

### 4. Enterprise Compliance & Security Hardening
- **Problem**: Prepare financial backend for SOC2/PCI-DSS compliance, removing hardcoded credentials and dynamic SQL.
- **1000x Execution**: Policy-derived static rules are integrated into the DoD harness, remediation is independently reviewed, and the receipt summarizes the executed checks. It supports—but does not itself constitute—compliance evidence or sign-off.

---

## Included Automation Scripts

- `plugins/1000x-engineer/skills/1000x-engineer/scripts/generate_run_receipt.py`: Runs manifest graders with secure argv execution and writes JSON/Markdown receipts plus hashes.
- `plugins/1000x-engineer/skills/1000x-engineer/scripts/extract_skill_trace.py`: Scaffolds a bounded CANDIDATE skill with path and overwrite protections.
- `plugins/1000x-engineer/skills/1000x-engineer/scripts/validate_skill.py`: Validates lifecycle files and frontmatter before activation.

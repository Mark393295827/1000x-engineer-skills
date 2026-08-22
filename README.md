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
├── .agents/
│   └── skills/
│       └── 1000x-engineer/            # Antigravity skill package
│           ├── SKILL.md               # Main 5-Step SOP entry point
│           ├── references/            # Deep-dive guides & architectural manuals
│           ├── resources/             # Templates for contracts, evals, and receipts
│           └── scripts/               # Automation scripts (receipts & skill distillation)
└── skills/
    └── 1000x-engineer/                # Standard workspace skills mirror
```

---

## The 5-Step SOP

1. **Forward Deploy & Trace Capture**: Extract real payloads, environment constraints, and runtime logs.
2. **Write Skills as Code**: Author formal Markdown contracts specifying I/O types, non-negotiable guarantees, and anti-patterns.
3. **Build Evals First**: Construct automated unit, property, and integration test suites before generating domain code.
4. **Launch Autonomous Loops**: Dispatch parallel subagents across decoupled architecture layers with closed feedback loops.
5. **Audit Receipts & Skillify**: Review machine-certified run receipts and distill edge-case resolutions into compounding skills.

---

## Included Automation Scripts

- `scripts/generate_run_receipt.py`: Runs test suites, type checkers, and linters, generating a certified `RUN_RECEIPT.md`.
  ```bash
  python skills/1000x-engineer/scripts/generate_run_receipt.py --spec "MyContract" --test-cmd "Unit Tests::pytest"
  ```
- `scripts/extract_skill_trace.py`: Distills debugging traces and resolutions into a structured skill template.
  ```bash
  python skills/1000x-engineer/scripts/extract_skill_trace.py --name "fix-issue" --desc "Activation description"
  ```

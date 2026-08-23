---
name: 1000x-engineer
description: >-
  Verified Autonomous Engineering Control Plane for bounded engineering work.
  Use when a task needs explicit authority, a contract, risk-matched graders,
  auditable evidence, safe multi-agent coordination, or reusable Skillify output.
---

# 1000x Engineer v1.0 — Verified Autonomous Engineering Control Plane

Evidence precedes mutation: no completion claim is stronger than the declared graders, their evidence, and the authority that permitted the work.

## Operating invariants

1. Evidence before mutation.
2. Contract before implementation.
3. Explicit authority before action.
4. Risk-matched graders before completion.
5. Least privilege and reversible changes by default.
6. Serial work before justified concurrency.
7. Stable interfaces before parallel work.
8. Independent verification before promotion.
9. Machine-readable, auditable evidence.
10. Skillify only verified and reusable knowledge.

## Five-step protocol

### 1. Preflight and trace

Record repository root, revision, branch, dirty state, environment, baseline, scope, and risk. Exit this stage only with a reproduction, a characterization, or an explicit diagnosis-only boundary.

### 2. Execution contract

Create a contract before implementation. It must declare mission, included/excluded/frozen scope, interfaces, invariants, forbidden actions, authority, budget, rollback, stop conditions, and definition of done. Use [the strict contract schema](./resources/task-contract.schema.json) and validate it with `scripts/validate_contract.py`.

### 3. Requirement-to-grader traceability

Map every material requirement to deterministic graders where possible. A grader manifest contains safe argument arrays, explicit timeouts, and a required flag. No normal execution path uses a command shell.

### 4. Bounded execution and routing

Use the state machine `PREFLIGHT → CONTRACTED → EVAL_READY → EXECUTING → VERIFYING → ACCEPTED | ABORTED`. Record failure signature, attempt count, changed diagnosis/strategy, and remaining budget/authority. Stop when the same failure signature, diagnosis, and strategy repeat.

Route by capability, not vendor model name:

| Tier | Capability | Use it for |
| --- | --- | --- |
| T0 | Deterministic tool | Search, formatting, static checks, tests, and exact transformations. |
| T1 | Fast agent | Narrow research, routine edits, and low-risk summarization. |
| T2 | General agent | Bounded implementation against a stable contract. |
| T3 | Reasoning agent | Architecture, difficult diagnosis, concurrency, and novel tradeoffs. |
| T4 | Independent evaluator | Fresh verification, review, and challenge of the proposed claim. |

Host adapters may map these capabilities to available tools or models. If a host lacks an override or subagent facility, inherit its default agent and execute serially.

### 5. Receipt, lifecycle, and Skillify

Generate `RUN_RECEIPT.json`, its authoritative `.sha256` sidecar, and a safe Markdown rendering. Completion requires: all mandatory task graders pass, no task-attributable regression is introduced, required evidence is complete, and no unresolved stop condition remains.

Promote skills only through `CANDIDATE → REVIEWED → EVAL_PASS → PUBLISHED` according to [the lifecycle policy](./references/lifecycle-policy.md). A `PUBLISHED` skill requires independent evaluation and release approval; this skill remains `REVIEWED` until those artifacts exist.

## Coordination model

Use a commander for authority and integration, a planner for contracts, workers for disjoint work packets, an integrator for joins, and an independent evaluator for final verification. Parallelize only after inputs, outputs, ownership, and join rules are stable. Failure routes are not normal join readiness.

## Canonical source and references

The plugin package containing this file is canonical. The `skills/` and `.agents/skills/` directories are generated compatibility mirrors; do not edit them by hand.

- [User Manual](./references/user-manual.md)
- [Unlock the Full Potential](./references/maximizing-potential-and-scenarios.md)
- [5-Step SOP Operational Guide](./references/sop-5-step-guide.md)
- [Software Factory Harness](./references/software-factory-harness.md)
- [Skillify Compounding Flywheel](./references/skillify-flywheel.md)
- [Host-neutral Routing Matrix](./references/model-routing-matrix.md)
- [Lifecycle Policy](./references/lifecycle-policy.md)
- [Regression Protocol](./references/regression.md)

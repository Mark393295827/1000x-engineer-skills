# Unlocking the Full Potential of 1000x Engineer

This guide shows how to move from using `1000x-engineer` as a checklist to operating a measurable, bounded, and continuously improving software factory.

Start with the [User Manual](./user-manual.md) if you have not yet completed a full five-step run.

> **Operating principle:** Full potential comes from better specifications, stronger evals, stable work boundaries, and lower coordination cost—not from maximizing agent count. “1000x” is a leverage target. Measure improvement on your own workloads instead of treating the name as a promised multiplier.

## 1. Use the leverage equation as a diagnostic

The skill’s conceptual equation is:

$$
\text{Engineering Leverage} =
\frac{\text{Specification Density} \times \text{Harness Rigor} \times \text{Useful Concurrency}}
{\text{Orchestration Tax}}
$$

The terms are not standardized measurements. Use them to locate the next constraint:

| Lever | Practical meaning | Observable proxy |
| --- | --- | --- |
| Specification density | Important decisions are explicit before execution. | Percentage of material requirements with schemas, examples, invariants, and acceptance checks. |
| Harness rigor | The grader suite detects meaningful defects reliably. | Requirement-to-grader coverage, mutation or seeded-defect detection, flake rate, clean rerun success. |
| Useful concurrency | Independent work finishes faster without increasing defects. | Parallel speedup reported beside conflict and integration-rework rates. |
| Orchestration tax | Time and cost spent coordinating, waiting, resolving overlap, and repairing integration. | Coordination plus integration plus rework as a share of total cycle time or cost. |

Improve the weakest term first. More workers amplify ambiguity and weak tests.

## 2. Pass the readiness gate before scaling

Score each dimension from 0 to 2:

| Dimension | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Outcome | Subjective or unclear. | Partly observable. | Measurable with explicit examples and counterexamples. |
| Baseline | Unknown. | Partially reproduced. | Reproducible with revision and environment recorded. |
| Boundaries | Overlapping and unstable. | Some seams identified. | Stable interfaces with owned and frozen surfaces. |
| Evals | None or manual only. | Partial automated checks. | Risk-matched deterministic graders cover material requirements. |
| Isolation | Work touches shared or live state. | Some fixtures or rollback. | Sandboxed fixtures, controlled dependencies, and tested rollback. |
| Authority | Mutation and release rights are implicit. | Some limits stated. | Read, write, external-action, merge, and deploy authority are explicit. |

Interpretation:

- **0–4:** stay in reconnaissance and contract design.
- **5–8:** run one bounded agent lane; strengthen missing gates.
- **9–10:** use two or three independent lanes with serial integration.
- **11–12:** consider wider concurrency if prior measurements show positive parallel efficiency.

This score is a local decision aid, not a universal benchmark.

## 3. Progress through the maturity ladder

| Level | Operating mode | Exit criterion |
| --- | --- | --- |
| 0 — Assisted | Apply the five-step checklist to one bounded task. | Scope and baseline are reproducible. |
| 1 — Contracted | Define inputs, outputs, invariants, negative constraints, authority, and Boolean DoD. | Another agent can explain what “done” means without guessing. |
| 2 — Harnessed | Establish acceptance, regression, boundary, integration, and static-analysis gates before mergeable implementation. | Required behavior is machine-gradable in an isolated environment. |
| 3 — Parallel | Convert the plan to a dependency graph and dispatch only independent work packets. | Speedup exceeds merge, conflict, and rework cost. |
| 4 — Verified | Run bounded repairs, targeted and full suites, independent evaluation, and a revision-tied receipt. | A clean-environment rerun reproduces the result. |
| 5 — Compounding | Turn reusable discoveries into versioned skills with regression evals and ownership. | Reuse reduces future lead time or escaped defects. |

Do not skip levels. A large agent fleet on a Level 0 task creates a faster path to inconsistent output.

## 4. Increase specification density

Use [`skill-contract-template.md`](../resources/skill-contract-template.md) as a starting point, then add the fields your risk profile requires.

### Contract quality test

A strong contract answers all of these:

1. What observable outcome must change?
2. What repository state and runtime evidence establish the baseline?
3. Which files, modules, interfaces, and systems are in scope?
4. Which surfaces are frozen?
5. What are the typed inputs, outputs, state transitions, and errors?
6. Which invariants must remain true?
7. Which implementation or operational patterns are forbidden?
8. Which commands or observations decide success?
9. What are the stop, escalation, rollback, and approval conditions?
10. Which evidence artifacts must be returned?

### Map every important claim to a grader

Create a small traceability table before execution:

| Requirement or invariant | Grader | Expected signal | Evidence artifact |
| --- | --- | --- | --- |
| Duplicate event produces one transition. | Concurrency integration test. | One durable side effect across repeated deliveries. | Full test log and fixture seed. |
| Existing clients remain compatible. | Contract snapshot suite. | No incompatible schema diff. | Snapshot diff. |
| No blocking call in async path. | Static rule plus load test. | Zero violations and latency below threshold. | Scanner and benchmark reports. |

If a material requirement has no grader, either add one or narrow the completion claim.

### Prefer behavioral boundaries

Tell workers what must remain true, not exactly which lines to type. Over-prescribing implementation reduces useful autonomy; under-specifying observable behavior creates guesswork. Schemas, examples, counterexamples, invariants, and tests form the productive middle.

## 5. Increase harness rigor

Use [`eval-harness-template.md`](../resources/eval-harness-template.md) and [`software-factory-harness.md`](./software-factory-harness.md) to build a layered quality firewall.

### Risk-to-grader matrix

| Risk | Useful graders |
| --- | --- |
| Local logic defect | Unit tests and table-driven cases. |
| Boundary or state-space defect | Property-based, fuzz, or metamorphic tests. |
| Persistence or service mismatch | Integration and contract tests. |
| Critical user journey regression | E2E tests. |
| Type or API drift | Strict type checks and schema diffing. |
| Style or structural defect | Linters and repository policy checks. |
| Security defect | Secret, dependency, static, dynamic, and access-control checks. |
| Performance regression | Reproducible latency, throughput, and resource thresholds. |
| Migration risk | Forward, rollback, reconciliation, and compatibility rehearsal. |
| Weak test suite | Mutation testing or seeded-defect detection. |

### Make runs reproducible

- Generate isolated fixtures per run.
- Pin and record dependency versions.
- Seed randomness and persist failing seeds.
- Inject clocks rather than reading wall time directly.
- Mock or record external network behavior.
- Keep test data free of secrets and personal information.
- Run a clean-checkout or clean-container verification for consequential changes.
- Preserve complete logs separately from the receipt.

### Keep some evaluation independent

When risk justifies it, give the evaluator the contract and changed artifact without the builder’s persuasive narrative. Use held-out or independently authored cases to reduce overfitting to visible tests.

## 6. Build a dependency graph before adding agents

Use this serial-to-parallel shape:

```text
Reconnaissance
    ↓
Contract and interface freeze
    ↓
Eval plan
    ↓
Independent work packets ──┬── Worker A
                           ├── Worker B
                           └── Worker C
    ↓
Serial integration
    ↓
Independent full verification
    ↓
Receipt and Skillify decision
```

### Work-packet contract

Every worker receives:

```text
Objective and deliverable:
Owned paths or interfaces:
No-touch paths or interfaces:
Inputs and upstream dependencies:
Expected output format:
Local grader commands:
Risk and authority boundaries:
Maximum attempts/time/cost:
Stop and escalation conditions:
Evidence to return:
```

### Test independence, not folder separation

Two tasks are safe to run concurrently only if they can progress against stable contracts without repeatedly changing each other’s inputs. “Database,” “API,” and “UI” are not independent while the schema is unsettled.

Start with two or three lanes. Increase only when these remain low:

- Conflicting edits.
- Interface churn.
- Duplicate investigation.
- Integration failures.
- Reviewer reconciliation time.
- Worker outputs rejected for missing context.

Keep one integration owner. Final joins, full-suite verification, and completion claims remain serial.

## 7. Route models and tools deliberately

Model names differ across hosts. Route by ambiguity, blast radius, reversibility, and verification strength rather than by code volume alone.

| Route | Best for | Avoid when |
| --- | --- | --- |
| Deterministic tool | Search, compilation, formatting, linting, schema generation, tests. | The task requires unresolved judgment. |
| Lite or fast model | Repetitive conversion, formatting, scaffolding, and narrow searches with strong graders. | Interfaces or requirements are ambiguous. |
| Balanced model | Localized implementation, tests, and refactors following established patterns. | Failure spans multiple layers or has high blast radius. |
| Deep-reasoning model | Architecture, interfaces, concurrency, migrations, security boundaries, and cross-layer diagnosis. | The task is fully mechanical and tool-solvable. |
| Independent evaluator | Acceptance, ambiguity, contradiction, and regression review. | It receives only the builder’s conclusion instead of artifacts and contract. |

Use the cheapest capable route, then escalate when evidence—not instinct—shows that the task exceeds it.

## 8. Control the autonomous repair loop

An autonomous loop needs a state and a budget:

```text
Trigger → Execute → Targeted Verify → Full Verify → Accept
                  ↘ Diagnose → Focused Repair ↗
```

Recommended controls:

1. Set a maximum attempt count per failure signature; two is a useful conservative default.
2. Record the diagnosis and intended change before each retry.
3. Retry only when the input, diagnosis, tool, scope, or strategy changes.
4. Rerun the targeted grader after a focused repair.
5. Rerun the entire required suite after targeted success.
6. Checkpoint evidence after each stable stage.
7. Stop on repeated signatures, expanding scope, missing authority, budget exhaustion, or environmental uncertainty.

More iterations do not compensate for a missing contract or a weak reproducer.

## 9. Strengthen the receipt trust model

The bundled [`generate_run_receipt.py`](../scripts/generate_run_receipt.py) is a v2 evidence generator. It records manifest graders, exit codes, durations, repository revision/dirty state, redacted logs, artifact hashes, and omitted checks. With no required grader, it reports `INSUFFICIENT_EVIDENCE`.

Its `VERIFIED` status means only that every required grader actually executed and exited zero. For material work, require explicit graders and augment the receipt with:

- Full revision and dirty-state information.
- Environment and dependency fingerprints.
- Requirement-to-grader mapping.
- Test totals, skips, coverage, mutation, and benchmark details.
- Links or paths to complete logs.
- Changed-artifact hashes.
- Clean-environment rerun evidence.
- Residual risk and omitted-check disclosures.
- Reviewer and approval receipts where required.

The generated Markdown file is editable. If immutability matters, store it in a signed commit, attach hashes or signatures, and preserve it in controlled CI or write-once storage.

In v1.0, the default helper executes manifest `argv` arrays with `shell=False`. Legacy shell strings require explicit `--allow-shell` and must be reviewed.

Receipt metadata and previews are escaped for Markdown and common secrets are redacted. Complete logs remain under `.evidence/logs`; review them and treat the receipt as evidence, not proof.

## 10. Make Skillify compound knowledge

Use [`skillify-flywheel.md`](./skillify-flywheel.md) to decide when a discovery is worth packaging. Strong candidates are recurring failure patterns, environment/tool quirks, reusable architectures, and previously hidden domain invariants.

The current [`extract_skill_trace.py`](../scripts/extract_skill_trace.py) is a bounded scaffolder. It does not parse a transcript, but it creates regression and activation eval placeholders, a lifecycle `STATUS`, and refuses unsafe names or overwrites by default. After running it:

1. Remove temporary names, paths, IDs, and one-off details.
2. Define precise positive and negative activation conditions.
3. State inputs, outputs, invariants, forbidden patterns, and stop conditions.
4. Add a minimal reproducer and regression eval.
5. Test correct activation, non-activation, and ambiguous cases in a fresh context.
6. Assign ownership, version, last-reviewed date, and deprecation criteria.
7. Measure whether reuse improves lead time or defect escape.

Do not Skillify every successful task. Excess low-quality skills increase discovery noise and maintenance cost.

## 11. Measure verified outcomes

Choose a small scorecard and establish a baseline before scaling:

| Metric | Definition | Why it matters |
| --- | --- | --- |
| Verified lead time | Contract accepted to clean full-harness pass, reported at p50 and p90. | Tracks delivery speed without ignoring verification. |
| First-pass yield | Integrated tasks passing the full harness on first attempt divided by completed tasks. | Reveals contract, implementation, and integration quality. |
| Escaped-defect rate | Post-merge defects attributable to the change per release or time window. | Prevents speed from masking quality loss. |
| Eval strength | Material requirement coverage plus mutation or seeded-defect detection. | Measures whether green tests are meaningful. |
| Reproducibility | Sampled receipts that rerun successfully from a clean environment. | Tests evidence durability. |
| Orchestration tax | Coordination, integration, and rework effort divided by total effort. | Shows when concurrency is counterproductive. |
| Cost per verified outcome | Model, tool, and infrastructure spend per accepted task. | Makes routing decisions economic. |
| Skill reuse value | Reuse count, time saved, false-trigger rate, and recurrence before/after. | Tests whether Skillify actually compounds. |

Interpret metrics together. A very high first-pass yield can mean excellent contracts—or weak graders. Faster lead time with rising escaped defects is not leverage.

## 12. Scenario playbooks

### A. Bounded feature

**Partition:** contract/schema, acceptance tests, implementation, documentation, independent evaluation.

**Gates:** unit, integration, compatibility, full regression, and relevant performance/security checks.

**Stop when:** product behavior is ambiguous or interface churn invalidates parallel work.

### B. Legacy refactor

**Partition:** dependency map, characterization tests, stable seams, per-domain transformations, migration/rollback, independent integration.

**Gates:** contract snapshots, data reconciliation, shadow or canary comparisons, and rollback rehearsal.

**Stop when:** existing behavior cannot be characterized or migration reversibility is unknown.

### C. Intermittent concurrency bug

**Partition:** trace capture, deterministic stress reproducer, state/lock model, minimal repair, independent stress evaluator.

**Gates:** seeded property tests, high-iteration stress, race/deadlock tooling, targeted and full regression.

**Stop when:** the failure cannot be reproduced or the proposed repair changes semantics outside the contract.

### D. Security or compliance hardening

**Partition:** policy-to-control map, threat model, scan lanes, remediation, and independent security review.

**Gates:** static, dependency, secret, dynamic, and access-control tests plus an evidence chain.

**Stop when:** a scanner result is being treated as certification or sensitive data would enter prompts or logs.

### E. Zero-to-one product

**Partition:** stabilize schemas and state transitions first; then separate persistence, services, UI, deployment, and E2E lanes.

**Gates:** critical user journeys, failure and rollback paths, observability, performance budgets, and deployment rehearsal.

**Stop when:** interfaces change faster than workers can integrate.

## 13. Thirty-day adoption plan

### Week 1 — Baseline and contract

- Choose one medium-sized feature or reproducible bug.
- Measure current lead time, repair count, and escaped defects if available.
- Use the mission brief and contract template.
- Run the workflow serially; learn where ambiguity appears.

### Week 2 — Harness and receipt

- Map material requirements to graders.
- Remove the most common source of flakiness.
- Add one clean-environment verification path.
- Generate receipts with explicit grader commands and preserve complete logs.

### Week 3 — Controlled parallelism

- Create a dependency graph and ownership matrix.
- Use two or three independent lanes.
- Measure conflicts, integration rework, speedup, and cost.
- Return to serial work if orchestration tax grows.

### Week 4 — Skillify and optimize

- Select one genuinely reusable discovery.
- Package it with trigger tests and a regression eval.
- Review model routing using cost per verified outcome.
- Decide whether to hold, expand, or reduce concurrency based on measured results.

## 14. Advanced prompt kit

### Commander prompt

```text
Use the 1000x-engineer skill.

Before mutation, return:
1. Baseline evidence and unknowns.
2. A contract with schemas, invariants, forbidden changes, and authority limits.
3. A requirement-to-grader matrix.
4. A dependency DAG and ownership matrix.
5. Iteration, time, cost, and stop budgets.

Execute only after those artifacts are internally consistent. Parallelize only
independent nodes. Keep integration and final verification serial. Finish with
the exact evidence supporting each completion claim, residual risks, and any
Skillify candidate. Do not merge or deploy unless explicitly authorized.
```

### Worker prompt

```text
Deliverable: <one bounded artifact>
Owned paths/interfaces: <exclusive territory>
No-touch paths/interfaces: <frozen territory>
Inputs/dependencies: <declared upstream artifacts>
Acceptance commands: <local graders>
Attempt limit: <N>
Stop conditions: <conditions>
Return: summary, changed artifacts, commands, results, risks, and integration notes.
Do not widen scope or certify the end-to-end task.
```

### Evaluator prompt

```text
Evaluate the artifact against the contract and graders without relying on the
builder’s conclusion. Look for omitted requirements, weak tests, contradictions,
unsafe authority expansion, and non-reproducible evidence. Return supported,
partially supported, or unsupported for each claim and identify the cheapest
additional check needed.
```

### Repair prompt

```text
Failure signature: <exact assertion/error>
Last diagnosis and change: <what changed>
Relevant artifact context: <minimal context>
Attempt: <n of max>

Diagnose before editing. Change strategy only if the evidence supports it. Apply
the smallest repair, rerun the targeted grader, then request the full suite. Stop
if the signature repeats or scope/authority must expand.
```

## 15. Non-negotiable guardrails

- Do not equate selected tests passing with correctness, security, production readiness, or compliance.
- Do not call the current receipt cryptographically immutable or tamper-proof.
- Do not eliminate risk-based human review for architecture, authentication, payments, cryptography, migrations, privacy, security, or compliance.
- Do not pass untrusted text into shell grader commands.
- Do not render or publish unsanitized receipt output from untrusted tests or tools; the helper does not escape Markdown.
- Do not place secrets or sensitive production payloads in prompts, logs, receipts, or extracted skills.
- Do not use parallelism without stable boundaries, exclusive ownership, and a serial integration owner.
- Do not retry an unchanged failure signature indefinitely.
- Do not Skillify a one-off workaround without a regression eval and trigger tests.
- Do not pass path-like or unvalidated values as a Skillify name; the scaffolder does not enforce kebab-case or output-directory containment.
- Do not commit, merge, deploy, spend, publish, or mutate external systems without the required authority.
- Do not promise a multiplier. Report measured before-and-after verified outcomes.

Full potential is reached when the workflow delivers faster verified outcomes with lower defect escape, acceptable cost, reproducible evidence, and reusable learning—not when it produces the most code or uses the most agents.

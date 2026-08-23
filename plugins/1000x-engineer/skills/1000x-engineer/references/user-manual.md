# 1000x Engineer User Manual

This manual explains how to use the `1000x-engineer` skill safely and effectively, from a first bounded task to a verified multi-agent workflow.

> **Positioning:** “1000x” is an ambition for engineering leverage, not a guaranteed productivity multiplier. The skill is an operating protocol, a set of templates, and two helper scripts. It does not itself provide an agent runtime, sandbox, model router, CI system, or deployment platform.

## 1. What the skill does

The skill turns a complex engineering objective into a five-stage operating loop:

1. **Trace capture in representative conditions (“Forward Deploy”)** — inspect the real repository and runtime before changing anything; this does not authorize a production release.
2. **Skills as Code** — define schemas, scope, invariants, forbidden changes, and measurable completion criteria.
3. **Evals first** — establish deterministic graders before production implementation.
4. **Bounded autonomous execution** — work serially by default, parallelize only independent work, and repair failures within explicit limits.
5. **Receipt and Skillify** — summarize verification evidence and capture reusable lessons.

The user remains the directly responsible individual for the objective, authorization boundaries, risk decisions, merge or deployment approval, and the adequacy of the graders.

### Good fits

- Multi-file features with observable acceptance criteria.
- Refactors where compatibility can be characterized and tested.
- Reproducible bugs, including intermittent concurrency failures.
- Security or compliance hardening with explicit policy checks.
- Full-stack work that can be separated behind stable interfaces.
- Repeated engineering work that should become a reusable skill.

### Use a simpler workflow when

- The change is trivial and local.
- The desired behavior is still a brainstorming question.
- No reliable acceptance check can be defined yet.
- The work cannot be isolated or rolled back safely.
- Parallel workers would edit the same unstable interfaces.

### Choose your path

| Goal | Start here |
| --- | --- |
| Learn safely | Run the [first-run quick start](#4-first-run-quick-start) in diagnosis-only mode. |
| Complete one bounded task | Follow all five quick-start steps with serial execution. |
| Scale to multiple agents | Pass the [advanced readiness gate](./maximizing-potential-and-scenarios.md#2-pass-the-readiness-gate-before-scaling), then use the work-packet contract. |
| Interpret or generate a receipt | Read [what PASS proves](#7-what-a-passing-receipt-proves) before running the helper. |
| Capture reusable knowledge | Use Skillify only after a verified run and complete its regression and trigger tests. |

### Terms used in this manual

- **Grader:** A command or observation with an expected signal that tests a requirement.
- **Material requirement:** A requirement whose violation would invalidate the outcome or create unacceptable risk.
- **Adequate harness:** A deterministic set of graders that directly covers the material requirements for the claim being made.
- **Stable interface:** A schema or behavioral boundary that workers can rely on without repeated incompatible changes during the run.
- **Failure signature:** The normalized error type, assertion, and relevant stack location used to decide whether a retry is making progress.
- **Dirty state:** Tracked or untracked working-tree changes not represented by the current commit.
- **Skillify candidate:** A reusable lesson worth scaffolding. It becomes a ready skill only after generalization, review, regression evals, and activation/non-activation tests.

## 2. Prerequisites and package layout

To use the operating protocol, you need an agent host that can discover `SKILL.md` packages. Git and a project-specific test toolchain are strongly recommended. Python 3 is required only for the bundled helper scripts; the skill itself is Markdown.

The complete package must retain this layout:

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Activation description and five-step protocol. |
| `references/` | Detailed SOP, harness, routing, Skillify, and advanced guidance. |
| `resources/` | Contract, eval-harness, and run-receipt templates. |
| `evals/` | Machine-readable positive, negative, and ambiguous activation cases. |
| `evidence/` | Lifecycle-gated review and later independent-evaluation evidence. |
| `scripts/generate_run_receipt.py` | Runs manifest grader argv arrays and writes a receipt plus final JSON sidecar hash. |
| `scripts/extract_skill_trace.py` | Scaffolds a new skill from supplied problem and solution fields. |

The sole canonical package is:

- `plugins/1000x-engineer/skills/1000x-engineer/`

The `.agents/skills/1000x-engineer/` and `skills/1000x-engineer/` directories are generated compatibility mirrors. Contributors edit only the canonical package, then run `python scripts/sync_compatibility_mirrors.py --prune` followed by `--check`.

When installing elsewhere, copy or install the entire `1000x-engineer` directory. Codex installations may discover user skills under `.agents/skills`, while the bundled skill installer in some environments uses `.codex/skills`. After installation, start a new task; if discovery still does not refresh, restart Codex.

In Codex, a portable installation request is:

```text
Install the skill from this project's plugins/1000x-engineer/skills/1000x-engineer directory.
```

### Verify a Codex installation

On Windows PowerShell:

```powershell
$skillCandidates = @(
  (Join-Path $env:USERPROFILE ".agents\skills\1000x-engineer"),
  (Join-Path $env:USERPROFILE ".codex\skills\1000x-engineer")
)
$skillCandidates | Where-Object {
  Test-Path -LiteralPath (Join-Path $_ "SKILL.md") -and
  Test-Path -LiteralPath (Join-Path $_ "lifecycle.json") -and
  Test-Path -LiteralPath (Join-Path $_ "evals\activation-cases.json")
}
```

On macOS or Linux, check both common user-scope locations:

```bash
test -f "$HOME/.agents/skills/1000x-engineer/SKILL.md" -a -f "$HOME/.agents/skills/1000x-engineer/lifecycle.json" || test -f "$HOME/.codex/skills/1000x-engineer/SKILL.md" -a -f "$HOME/.codex/skills/1000x-engineer/lifecycle.json"
```

If your Codex home is customized, use that configured location instead.

## 3. Activate the skill

Explicit activation is the most portable approach:

```text
Use the 1000x-engineer skill and execute its five-step SOP.
Mission: make webhook processing idempotent without changing the public API.
```

Auto-activation depends on the host recognizing the `name` and `description` in `SKILL.md`.

### Recommended mission brief

For non-trivial work, give the agent this contract-shaped prompt:

```text
Use the 1000x-engineer skill and execute its five-step SOP.

OUTCOME
<Observable user or business outcome>

EVIDENCE FIRST
Inspect the live repository, runtime, logs, dependencies, and existing tests.
Record the baseline and reproduce the current behavior before mutation.

SCOPE
In scope: <paths, modules, interfaces>
Frozen/out of scope: <paths, modules, interfaces>
Authorized actions: <read, edit, test, commit, deploy, and so on>

CONTRACT
Inputs and outputs: <schemas or examples>
Invariants: <rules that must remain true>
Forbidden changes: <negative constraints>
Compatibility and rollback requirements: <requirements>

DEFINITION OF DONE
Required graders: <exact commands>
Performance or security thresholds: <thresholds>
Required evidence: <receipt, logs, coverage, screenshots, benchmarks>

EXECUTION CONTROLS
Parallelize only independent work with explicit ownership.
Maximum repair attempts per failure class: <N>
Stop before destructive actions, external publication, deployment, credential use,
or material scope expansion unless explicitly authorized.

DELIVERABLES
<Changed artifacts, verification evidence, RUN_RECEIPT.md, Skillify candidates>
```

The clarity of this brief matters more than its length. Omit fields that genuinely do not apply; do not leave important authority or acceptance decisions implicit.

## 4. First-run quick start

For a first orientation, choose **diagnosis-only** on a bounded bug: inspect and reproduce without modifying files. For a first complete run, choose a reproducible bug or medium-sized feature in a repository with existing tests.

The first 15 minutes should produce a protected baseline, a compact contract, an eval plan, and a decision to proceed or stop. Implementation and final verification take as long as the task and native test suite require. Default to **one serial execution lane** on the first run.

### Step 1 — Trace capture and safe preflight

**Run in PowerShell from the target repository:**

```powershell
git rev-parse --show-toplevel
git status --short --branch
git log -n 1 --oneline
python --version
```

Use `py`, `python3`, `uv`, Poetry, or another launcher if that is what the project documents. Python is needed for the bundled helpers; the project’s own runtime may differ.

**Send to Codex:**

```text
Use the 1000x-engineer skill in read-only preflight mode.
Confirm the repository root. Read the project instructions and manifests, identify
its native setup and test commands, inspect the current Git state, and list baseline
failures and unknowns. Treat every pre-existing or unexplained dirty path as frozen.
Do not edit, reset, clean, overwrite, commit, merge, deploy, or access credentials.
```

Use the project’s documented test runner, not a generic command copied from this manual:

- If a failing test already exists, run its exact target or node ID.
- If no test exists, ask Codex to propose a minimal failing regression test or read-only reproducer; explicitly authorize that test-only edit before production changes.
- If reproduction remains impossible, stop at diagnosis and narrow the claim.
- If the baseline suite is already red, record unrelated failures and require that the task introduce no new ones. Do not claim the full suite is healthy.

Record the revision, dirty state, relevant runtime versions, reproduction, in-scope and frozen paths, known risks, and missing evidence in the task. Save them to a repository artifact only if the project has an appropriate documented location.

### Step 2 — Create one task contract

Use [`skill-contract-template.md`](../resources/skill-contract-template.md) as the expanded reference. For the first run, ask Codex to return one compact contract in the task; this is the source of truth for scope, authority, and verification.

**Send to Codex:**

```text
Using the baseline, draft one task contract with: outcome; inputs and outputs;
in-scope and frozen paths; invariants; forbidden changes; authorized actions;
rollback; stop conditions; and a requirement-to-grader table. Do not edit files yet.
```

Example contract excerpt:

```markdown
# Idempotent Webhook Contract

Goal: duplicate deliveries for the same event ID produce one state transition.

Invariants:
- Existing endpoint and response schema remain compatible.
- A replay returns the stored result without repeating side effects.
- No lock remains held after an exception.

Forbidden:
- No process-local-only lock for distributed workers.
- No raw SQL string construction.

Done when:
- Duplicate and concurrent delivery tests pass.
- Existing webhook regressions show no new failures.
- The repository’s required static gates pass.
```

Review the contract and eval plan. Explicitly tell Codex when it may begin file changes; until then the workflow remains read-only.

### Step 3 — Establish the eval plan

Use [`eval-harness-template.md`](../resources/eval-harness-template.md) for a durable harness. Map every material requirement—one whose violation would invalidate the outcome or create unacceptable risk—to at least one grader.

Examples only; substitute the repository’s documented commands:

```powershell
python -m pytest tests\path\test_module.py::test_case -q
python -m pytest tests\ -q
mypy src\ --strict
ruff check src\ tests\
```

`mypy` and `ruff` are examples, not universal requirements. Use them only when installed or explicitly added to the contract. Add property, integration, E2E, security, performance, migration, or rollback graders when the risk requires them.

Make verification deterministic where practical: isolate fixtures, pin dependencies, seed randomness, inject clocks, mock network calls, and preserve full logs.

### Step 4 — Execute a bounded loop

**Serial execution is the default.** Spawn workers only when the readiness gate in the [advanced guide](./maximizing-potential-and-scenarios.md#2-pass-the-readiness-gate-before-scaling) shows stable, genuinely independent work packets. At readiness 9–10, start with two or three lanes; keep one serial integration owner.

For each lane, declare:

```text
Deliverable:
Owned paths or interfaces:
No-touch paths:
Inputs and dependencies:
Expected output:
Local grader commands:
Risks and stop conditions:
Evidence to return:
```

When a grader fails:

1. Capture the exact failure signature: the normalized assertion, error type, and relevant stack location.
2. Record the diagnosis and planned change.
3. Make a focused repair.
4. Rerun the targeted grader.
5. Stop and escalate if the signature repeats without a materially changed diagnosis, input, tool, scope, or strategy.

Local and targeted checks belong in this repair loop. The receipt helper in Step 5 will rerun the declared final suite and capture that run. A worker never certifies the end-to-end task.

### Step 5 — Run final graders, review the receipt, and decide whether to Skillify

The receipt helper **executes the supplied argv arrays again** from the verified repository root and creates `RUN_RECEIPT.json`, `RUN_RECEIPT.md`, and a JSON hash. Before running it:

- Use a JSON manifest with `argv` arrays. The default execution path is `subprocess.run(..., shell=False)`.
- Supply every meaningful grader explicitly. With none, the status is `INSUFFICIENT_EVIDENCE`, never `VERIFIED`.
- Confirm that replacing the chosen output path is acceptable; the JSON receipt is the machine-readable source.
- Expect a 300-second timeout per grader and a 2,000-character Markdown preview; complete redacted logs are stored under `.evidence/logs`.

**Run in PowerShell from the target repository root, resolving either common user-scope installation:**

```powershell
$skillRoot = @(
  (Join-Path $env:USERPROFILE ".agents\skills\1000x-engineer"),
  (Join-Path $env:USERPROFILE ".codex\skills\1000x-engineer")
) | Where-Object {
  Test-Path -LiteralPath (Join-Path $_ "SKILL.md") -and
  Test-Path -LiteralPath (Join-Path $_ "lifecycle.json") -and
  Test-Path -LiteralPath (Join-Path $_ "evals\activation-cases.json")
} | Select-Object -First 1
if (-not $skillRoot) { throw "1000x-engineer is not installed in a recognized user-scope location" }
$receiptScript = Join-Path $skillRoot "scripts\generate_run_receipt.py"
python $receiptScript --repo-root (Get-Location) --manifest "grader-manifest.json" --spec "Idempotent-Webhooks" --scope "services/webhooks"
```

Replace the sample graders with the project’s required native commands. Omit the Ruff grader if Ruff is not a declared project gate. If you are working inside this skill’s source checkout, use `plugins/1000x-engineer/skills/1000x-engineer/scripts/generate_run_receipt.py`; resolve that canonical script path before changing to the target repository root.

On macOS or Linux, resolve the same two locations:

```bash
skill_root="$HOME/.agents/skills/1000x-engineer"
test -f "$skill_root/SKILL.md" || skill_root="$HOME/.codex/skills/1000x-engineer"
test -f "$skill_root/SKILL.md" || { echo "1000x-engineer is not installed" >&2; exit 1; }
python3 "$skill_root/scripts/generate_run_receipt.py" --repo-root "$PWD" --manifest "grader-manifest.json" --spec "Idempotent-Webhooks" --scope "services/webhooks"
```

Review the receipt against the contract, inspect omitted checks and residual risks, and apply the required human approval before merge or deployment.

Skillify is an optional post-run activity inside Stage 5, not a sixth workflow step. Create only a **candidate scaffold** for a genuinely reusable discovery; a skill is not ready to install until it has been generalized, reviewed, given a regression eval, and tested for correct activation and non-activation. See the [utility reference](#extract-skill-trace-utility) and [advanced Skillify guide](./maximizing-potential-and-scenarios.md#10-make-skillify-compound-knowledge).

## 5. Detailed five-step operating guide

| Stage | Operator action | Required output | Exit gate |
| --- | --- | --- | --- |
| 1. Trace | Inspect state, reproduce behavior, map boundaries. | Baseline evidence and scoped problem statement. | Current behavior is reproducible or uncertainty is explicitly recorded. |
| 2. Contract | Define schemas, invariants, forbidden changes, authority, and DoD. | Task contract. | Another agent can explain what “done” means without guessing. |
| 3. Evals | Build acceptance and regression graders before mergeable implementation. | Deterministic harness and baseline results. | Material requirements map to checks with known expected signals. |
| 4. Execute | Build a dependency graph, assign exclusive ownership, run bounded repairs. | Integrated change plus worker evidence. | Targeted and local checks pass; the integrated state is ready for final graders. |
| 5. Receipt | Run final graders, record results, and decide whether to Skillify. | Receipt, complete logs, residual risks, reusable lesson decision. | Required graders ran after the last material edit, evidence matches the claim, and risk-appropriate human review is complete. |

### Stage 1: Trace capture in representative conditions

The skill calls this “Forward Deploy,” meaning getting close to the real operating conditions. It does not authorize an unreviewed production change or release. Prefer read-only inspection, sanitized logs, representative payloads, and a local or staging reproducer. Keep secrets and personal data out of prompts and receipts.

If the failure cannot be reproduced, narrow the claim to diagnosis and evidence gathering. Do not let the autonomous loop optimize against a guessed failure.

### Stage 2: Skills as Code

A high-density contract reduces back-and-forth by encoding the decisions that otherwise live in the operator’s head. Strong contracts specify behavior at boundaries rather than prescribing every implementation line.

Use examples and counterexamples. For every invariant, ask: “What test would fail if this rule were violated?” If there is no answer, the rule may be too vague or the harness may be incomplete.

### Stage 3: Evals first

“Evals first” means no mergeable production implementation before an adequate acceptance harness. Throwaway probes may still be useful to understand an unknown system, but they do not replace the baseline or final graders.

Use the cheapest check that detects the risk:

- Unit tests for local logic.
- Property or boundary tests for state spaces and concurrency.
- Integration tests for persistence and service contracts.
- E2E tests for critical user journeys.
- Type and lint tools for structural defects.
- Security, performance, migration, and rollback checks for relevant risks.

### Stage 4: Autonomous execution

Concurrency is an optimization, not a maturity badge. Work serially until the contract, interfaces, and evals are stable. At readiness 9–10, start with two or three independent lanes and increase only when measured speedup exceeds coordination and integration cost.

Good boundaries are stable contracts, not merely different folders. Database, API, and UI workers are not independent while the schema is still changing. Freeze or version the interface first.

Set explicit limits for attempts, elapsed time, model/tool spend, and authorized actions. Repeated failure is evidence that the contract, harness, or architecture needs human attention.

### Stage 5: Receipt and Skillify

A receipt is useful only when its graders cover the claim. Pair it with the exact revision, complete logs, environment details, and any residual risk. For high-impact changes, preserve risk-based code review, security review, migration approval, and deployment controls.

Skillify is successful when the new skill measurably improves a future task. A scaffold with no trigger tests or regression eval is unfinished knowledge, not a compounding asset.

## 6. Bundled utility reference

### `generate_run_receipt.py`

Supported arguments:

| Argument | Meaning |
| --- | --- |
| `--spec` | Contract or task name. |
| `--scope` | Target module or path. |
| `--manifest` | JSON manifest containing `version: 2` and grader objects with `id`, `argv`, `timeout_seconds`, and `required`. |
| `--repo-root` | Verified repository root used as grader `cwd`; defaults to the current directory. |
| `--output-dir` | Contained output directory for JSON, Markdown, hash, and redacted logs. |
| `--contract` | Optional strict task-contract JSON. It blocks grader execution if testing is unauthorized or timeout budget is exceeded. |

Current behavior and limits:

- Each manifest grader is an argument vector with an explicit timeout and `shell=False`.
- Commands run sequentially and pass only when their exit code is zero.
- If no required grader is supplied, the status is `INSUFFICIENT_EVIDENCE`.
- The JSON receipt records schema version, repository commit/branch/dirty state, environment, requirement outcomes, graders, hashes, omitted checks, and residual risks.
- The Markdown rendering escapes pipes/backticks and redacts common secrets. It is an editable evidence summary, not cryptographic proof or tamper protection.
- A required grader or mandatory requirement failure is `FAILED`; an execution error is `ABORTED`; all required graders and mandatory requirements passing is `VERIFIED`.
- `RUN_RECEIPT.json.sha256` is the authoritative SHA-256 of the final JSON receipt. There is no embedded self-hash.
- Shell-string execution is not supported. Convert each check into an explicit `argv` array.

If a check takes more than five minutes, intentionally shard it into truthful subcommands that fit the limit or run and preserve it separately, then disclose that it is not captured by this helper.

### Extract Skill Trace utility

Supported required arguments are `--name` and `--desc`. Optional arguments describe the title, problem, root cause, solution, and output directory.

Despite its name, the script does not parse a transcript or log file. It scaffolds a CANDIDATE package from the CLI fields you provide, including `SKILL.md`, regression and activation evals, `regression.yaml`, and `STATUS`. It refuses to overwrite an existing target unless `--overwrite` is explicit.

The script enforces kebab-case (`^[a-z0-9]+(?:-[a-z0-9]+)*$`, 1–64 characters) and guarantees that the resolved target remains inside `--out-dir`.

On Windows, first confirm that the target skill directory does not exist, resolve the installed skill root, then run:

```powershell
$skillName = "fix-webhook-idempotency-race"
if ($skillName -notmatch '^[a-z0-9]+(-[a-z0-9]+)*$') { throw "Unsafe skill name: $skillName" }
$skillTarget = Join-Path (Get-Location) ".agents\skills\$skillName"
if (Test-Path -LiteralPath $skillTarget) { throw "Skill target already exists: $skillTarget" }
$skillRoot = @(
  (Join-Path $env:USERPROFILE ".agents\skills\1000x-engineer"),
  (Join-Path $env:USERPROFILE ".codex\skills\1000x-engineer")
) | Where-Object {
  Test-Path -LiteralPath (Join-Path $_ "SKILL.md") -and
  Test-Path -LiteralPath (Join-Path $_ "lifecycle.json") -and
  Test-Path -LiteralPath (Join-Path $_ "evals\activation-cases.json")
} | Select-Object -First 1
if (-not $skillRoot) { throw "1000x-engineer is not installed in a recognized user-scope location" }
python (Join-Path $skillRoot "scripts\extract_skill_trace.py") --name $skillName --desc "Use when concurrent duplicate webhook deliveries can race before transaction commit." --problem "Duplicate workers perform the same side effect." --root-cause "The read-before-write sequence lacks a cross-worker guard." --solution "Acquire a bounded lock with TTL; re-read state; perform one transition; release in finally; run the concurrency regression test." --out-dir ".agents\skills"
```

The generated package is a candidate. Review it, add a regression eval, test positive and negative activation cases, and version it before installation.

## 7. What a passing receipt proves

A `VERIFIED` receipt proves only that every required manifest grader actually executed and returned exit code zero during that run. An empty or optional-only manifest is `INSUFFICIENT_EVIDENCE`, not verification.

It does not, by itself, prove:

- That omitted requirements were tested.
- That the tests are correct or sufficiently strong.
- That the environment matches production.
- That security, privacy, performance, or compliance requirements are satisfied.
- That the receipt has not been edited.
- That deployment or merge is authorized.

For stronger evidence, add requirement-to-grader mapping, test counts, coverage or mutation results, artifact hashes, full-log links, environment fingerprints, clean-checkout reruns, and independent review.

## 8. Common prompt recipes

### Read-only diagnosis

```text
Use the 1000x-engineer skill in diagnosis-only mode.
Inspect the live state, reproduce the failure, identify the most likely root cause,
and report evidence and unknowns. Do not modify files or external systems.
```

### Bug repair

```text
Use the 1000x-engineer SOP. First create a deterministic failing test or reproducer.
Then make the smallest fix, rerun the targeted grader, rerun the complete regression
suite, and produce a receipt. Stop after two repeated failure signatures and report
the missing assumption instead of retrying blindly.
```

### Compatibility-preserving refactor

```text
Use the 1000x-engineer SOP for this refactor. Build characterization tests and
interface snapshots first. Freeze public behavior, partition work only at stable
seams, require a rollback path, and have an independent evaluator run the full suite.
```

### Multi-agent feature

```text
Use the 1000x-engineer SOP. Before spawning workers, return a dependency DAG and
ownership matrix. Give each worker exclusive paths or interfaces, local graders,
no-touch boundaries, a repair limit, and an evidence schema. Keep integration and
final verification serial under one owner.
```

### Worked first-run example: ordinary Python bug

Assume an issue says that `parse_retry_count("")` should return the documented default instead of raising an exception.

1. **Read-only preflight:** Codex finds the repository instructions, reports an unrelated dirty documentation file, freezes it, and identifies `python -m pytest` as the native runner.
2. **Reproduce:** If an exact failing test already exists, run it. If none exists, authorize only a minimal regression-test edit, confirm that it fails for the expected reason, and keep production code unchanged.
3. **Contract:** Scope the task to the parser and its test. Freeze public configuration syntax, require the documented default, forbid unrelated cleanup, and map the behavior to the regression test plus the repository’s required static gates.
4. **Approve mutation:** Review the contract, then explicitly authorize the focused production edit. Use one serial lane; this task has no useful independent work packet.
5. **Repair and verify:** Make the smallest change, rerun the exact regression test, then use the receipt helper to run and capture the declared final suite.

If the full baseline was already red, compare final failures with the recorded baseline. A targeted fix may be supported, but do not produce or describe a full-suite `PASS` while unrelated failures remain. Report the narrower verified claim and the unresolved baseline failures.

## 9. Troubleshooting

| Symptom | Cause | Action |
| --- | --- | --- |
| The skill does not activate. | Host discovery did not refresh or auto-trigger. | Verify the complete package path, begin a new turn, and invoke `1000x-engineer` explicitly. |
| A named worker capability is “not a command.” | Reference terminology describes host capabilities, not shell executables. | Use your agent platform’s native team or worker mechanism, or work serially. |
| Receipt is `INSUFFICIENT_EVIDENCE`. | No manifest or no required grader was supplied. | Add every required grader to the manifest and rerun. |
| Receipt is missing important output. | Per-stream logs are truncated. | Keep complete CI or local logs as separate artifacts. |
| Git SHA is wrong or absent. | Script ran outside the target Git repository. | Run it from the target repository root. |
| A grader times out. | The command exceeded 300 seconds. | Run it directly to diagnose, then shard or wrap it with a bounded, truthful status command. |
| Agents overwrite each other. | Ownership or interfaces overlap. | Stop, re-partition the graph, freeze shared contracts, and integrate serially. |
| Tests are flaky. | Time, randomness, network, dependencies, or fixtures are uncontrolled. | Isolate fixtures, pin dependencies, seed randomness, freeze clocks, and mock networks. |
| Repair loops do not converge. | The diagnosis or contract has not changed. | Stop at the iteration limit; revisit assumptions, scope, and architecture. |
| Skillify aborted or reported conflict. | The target skill directory already exists and `--overwrite` was not passed. | Inspect the existing directory, choose a new `--name` or `--out-dir`, or supply `--overwrite` intentionally. |

## 10. End-of-run operator checklist

- [ ] The final claim is narrower than or equal to the verified scope.
- [ ] Required graders ran after the last material change.
- [ ] Targeted checks and the full required suite passed.
- [ ] Revision, dirty state, environment, and complete logs are preserved.
- [ ] Residual risks and omitted graders are explicit.
- [ ] Destructive, external, merge, and deployment actions had the required approval.
- [ ] Rollback is ready for high-blast-radius changes.
- [ ] Any Skillify candidate is reusable, tested, versioned, and reviewed.

## 11. Further reading

- [`sop-5-step-guide.md`](./sop-5-step-guide.md) — detailed five-stage procedure.
- [`software-factory-harness.md`](./software-factory-harness.md) — deterministic harness design.
- [`model-routing-matrix.md`](./model-routing-matrix.md) — model tiers and agent topology.
- [`skillify-flywheel.md`](./skillify-flywheel.md) — when and how to distill reusable knowledge.
- [`maximizing-potential-and-scenarios.md`](./maximizing-potential-and-scenarios.md) — maturity model, metrics, and advanced playbooks.
- [`skill-contract-template.md`](../resources/skill-contract-template.md) — task contract scaffold.
- [`eval-harness-template.md`](../resources/eval-harness-template.md) — Definition of Done scaffold.
- [`run-receipt-template.md`](../resources/run-receipt-template.md) — expanded receipt example.

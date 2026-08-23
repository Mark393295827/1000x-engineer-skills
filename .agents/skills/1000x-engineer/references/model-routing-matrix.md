# Host-neutral routing and coordination matrix

Route work by the capability needed to produce reliable evidence, not by a vendor model label. A host adapter may map these tiers to its own tools or agents; the mapping is deliberately non-normative.

| Tier | Capability | Authority default | Suitable work | Escalate when |
| --- | --- | --- | --- | --- |
| T0 | Deterministic tool | Read/test only | File search, formatting, parsing, tests, linters, type checks. | Output is ambiguous or a design decision is needed. |
| T1 | Fast agent | Read-only first | Bounded discovery, narrow summaries, mechanical drafts. | It encounters a novel invariant, conflict, or unsafe action. |
| T2 | General agent | Contract-limited edit/test | Local implementation and regression repair against stable interfaces. | The task crosses ownership or interfaces. |
| T3 | Reasoning agent | Contract-limited edit/test | Architecture, concurrency, complex diagnosis, evaluator design. | Evidence is insufficient or independent challenge is required. |
| T4 | Independent evaluator | Read/test only | Fresh review, reproduction, and verification of the completion claim. | It finds a gap, regression, or stop condition. |

## Dispatch rules

1. Prefer T0 when a deterministic tool can answer the question.
2. Start serially. Add parallel workers only after stable interfaces, exclusive ownership, and a typed join contract exist.
3. A worker receives a work packet: scope, inputs, outputs, invariants, forbidden actions, authority, graders, stop conditions, and evidence to return.
4. The integrator alone resolves cross-boundary conflicts and invokes final graders.
5. T4 must not be the same execution path that made the material change when independent verification is required.

## Host adapter guidance

Use the host's native mechanism for model selection, subagents, worktrees, and tool calls. If any mechanism is unavailable, do not emulate it with brittle shell tricks: inherit the host default, preserve the contract, and work serially. Host-specific adapters belong outside this canonical skill package.

## Readiness before concurrency

| Readiness signal | Required before parallel work |
| --- | --- |
| Interfaces | Inputs, outputs, and compatibility boundaries are frozen or versioned. |
| Ownership | Each worker has disjoint files or a documented coordination owner. |
| Evaluation | Shared graders and expected signals are known. |
| Join | Integration order and conflict resolution are explicit. |
| Authority | Each worker has only the minimum permissions needed. |

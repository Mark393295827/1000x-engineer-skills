# Skill lifecycle policy

The lifecycle is evidence-gated, not a cosmetic label.

```text
CANDIDATE → REVIEWED → EVAL_PASS → PUBLISHED
```

| Status | Minimum evidence | May do | Must not claim |
| --- | --- | --- | --- |
| `CANDIDATE` | Package scaffold and regression/activation plans. | Be reviewed and improved. | Production readiness or validated activation. |
| `REVIEWED` | Maintainer review record, synchronized status, declared graders, and activation-case suite. | Run local and CI validation. | Independent evaluation or release approval. |
| `EVAL_PASS` | Recorded activation outcomes, regression results, and an independent evaluator record. | Be proposed for release. | Publication without release approval. |
| `PUBLISHED` | `EVAL_PASS` evidence plus explicit release approval and matching release version. | Be distributed as published. | Safety beyond its evaluated scope. |

`validate_skill.py` enforces status agreement across `STATUS`, `regression.yaml`, and `lifecycle.json`. It also rejects promotion when the required evidence files are absent or structurally incomplete.

An activation case that requests destructive work without authority is a **positive** activation: the skill should activate its safety protocol and stop before mutation. It is not a negative activation.

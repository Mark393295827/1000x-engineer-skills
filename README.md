# 1000x Engineer v1.0 — Verified Autonomous Engineering Control Plane

![1000x Engineer Command Center](promo/assets/banner.jpg)

1000x Engineer turns bounded engineering work into explicit contracts, safe deterministic checks, auditable receipts, and reusable skills. “1000x” is a leverage target, not a claimed multiplier.

## Canonical package

The only hand-maintained source is [`plugins/1000x-engineer/skills/1000x-engineer`](plugins/1000x-engineer/skills/1000x-engineer). The legacy [`skills/1000x-engineer`](skills/1000x-engineer) and [`.agents/skills/1000x-engineer`](.agents/skills/1000x-engineer) packages are generated compatibility mirrors.

Synchronize mirrors after a canonical edit:

```bash
python scripts/sync_compatibility_mirrors.py --prune
python scripts/sync_compatibility_mirrors.py --check
```

## What it enforces

- Safe grader manifests: `argv` arrays, `shell=False`, explicit timeout and required flags.
- Receipt states: `VERIFIED`, `FAILED`, `INSUFFICIENT_EVIDENCE`, and `ABORTED`.
- Final receipt integrity: `RUN_RECEIPT.json.sha256` is the authoritative hash of the final JSON file.
- Strict execution contracts: authority, scope, budgets, rollback, stop conditions, and definition of done.
- Skill lifecycle: `CANDIDATE → REVIEWED → EVAL_PASS → PUBLISHED` with evidence gates.
- Capability routing: T0 deterministic tool, T1 fast agent, T2 general agent, T3 reasoning agent, T4 independent evaluator.

## Documentation

- [User Manual](plugins/1000x-engineer/skills/1000x-engineer/references/user-manual.md)
- [Unlock the Full Potential](plugins/1000x-engineer/skills/1000x-engineer/references/maximizing-potential-and-scenarios.md)
- [Routing Matrix](plugins/1000x-engineer/skills/1000x-engineer/references/model-routing-matrix.md)
- [Lifecycle Policy](plugins/1000x-engineer/skills/1000x-engineer/references/lifecycle-policy.md)

## First verified receipt

Create a manifest inside the target repository:

```json
{
  "version": 2,
  "graders": [
    {
      "id": "tests",
      "argv": ["python", "-m", "pytest", "tests"],
      "timeout_seconds": 300,
      "required": true
    }
  ]
}
```

Then run the canonical helper from the target repository root:

```bash
python /path/to/plugins/1000x-engineer/skills/1000x-engineer/scripts/generate_run_receipt.py \
  --repo-root . --manifest grader-manifest.json --spec "Target change" --scope "src/target"
```

For contract-bound work, supply a validated contract as well:

```bash
python plugins/1000x-engineer/skills/1000x-engineer/scripts/validate_contract.py \
  plugins/1000x-engineer/skills/1000x-engineer/resources/task-contract.example.json
```

`--contract` prevents graders from running when the contract does not authorize tests or its declared timeout budget is exceeded. It does not grant merge, deployment, credential, or network authority.

## Verification

```bash
python -m pytest
python -m ruff check .
python -m mypy plugins/1000x-engineer/skills/1000x-engineer/scripts scripts tests
python scripts/sync_compatibility_mirrors.py --check
python plugins/1000x-engineer/skills/1000x-engineer/scripts/validate_skill.py plugins/1000x-engineer/skills/1000x-engineer
```

The repository is `REVIEWED`, not `PUBLISHED`: independent activation evaluation, an independent evaluator record, and release approval are intentionally required before promotion.

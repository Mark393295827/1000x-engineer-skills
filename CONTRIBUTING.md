# Contributing

1. Create a focused branch from `main`.
2. Write or update the contract and requirement-to-grader mapping before implementation.
3. Edit only `plugins/1000x-engineer/skills/1000x-engineer`. Generate its compatibility mirrors with `python scripts/sync_compatibility_mirrors.py --prune`, then prove byte-level consistency with `python scripts/sync_compatibility_mirrors.py --check`.
4. Run `python -m pytest`, contract and skill validation, plugin validation, and the security checks locally.
5. Include the JSON receipt, Markdown rendering, omitted checks, and residual risks in the pull request.

Changes that broaden authority, add network access, or introduce destructive operations require explicit reviewer approval.

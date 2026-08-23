# Contributing

1. Create a focused branch from `main`.
2. Write or update the contract and requirement-to-grader mapping before implementation.
3. Keep `plugins/1000x-engineer/skills/1000x-engineer` canonical. Compatibility mirrors under `skills/` and `.agents/` must be synchronized, not edited independently.
4. Run `python -m pytest`, the skill validator, plugin validation, and the security checks locally.
5. Include the JSON receipt, Markdown rendering, omitted checks, and residual risks in the pull request.

Changes that broaden authority, add network access, or introduce destructive operations require explicit reviewer approval.

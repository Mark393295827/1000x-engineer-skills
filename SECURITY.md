# Security policy

The plugin is designed for least-privilege, reviewable engineering workflows. It does not grant authority to mutate repositories, publish releases, or access external systems.

## Reporting

Please report a reproducible security issue privately to the repository owner before opening a public issue. Include the affected commit, operating system, reproduction steps, and impact. Never include real credentials or private customer data; redact them and use placeholders.

## Supported line

The `v1.0.x` line receives security fixes while it is the current stable line. Receipts and logs are evidence artifacts, not a promise that a task is safe or correct.

## Safe defaults

- Grader manifests use argument arrays and `shell=False`.
- Shell execution is a legacy, explicit opt-in only.
- Skillify rejects traversal, invalid names, and overwrites by default.
- Secrets are redacted from receipt previews and stored logs.

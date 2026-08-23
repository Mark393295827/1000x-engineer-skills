#!/usr/bin/env python3
"""Small repository-local plugin validation used by CI and release checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    plugin = Path(sys.argv[1] if len(sys.argv) > 1 else "plugins/1000x-engineer").resolve()
    manifest_path = plugin / ".codex-plugin/plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid plugin manifest: {exc}", file=sys.stderr)
        return 1
    errors = []
    for field in ("name", "version", "description", "skills"):
        if not manifest.get(field):
            errors.append(f"missing manifest field: {field}")
    skills_root = (plugin / manifest.get("skills", "./skills/")).resolve()
    if not skills_root.is_dir():
        errors.append(f"missing skills directory: {skills_root}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"valid plugin: {plugin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

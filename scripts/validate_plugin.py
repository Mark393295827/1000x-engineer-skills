#!/usr/bin/env python3
"""Small repository-local plugin validation used by CI and release checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    plugin = Path(args[0] if args else "plugins/1000x-engineer").resolve()
    manifest_path = plugin / ".codex-plugin/plugin.json"
    try:
        raw = manifest_path.read_text(encoding="utf-8")
        manifest = json.loads(raw)
        if not isinstance(manifest, dict):
            raise ValueError("plugin manifest must be a JSON object")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"invalid plugin manifest: {exc}", file=sys.stderr)
        return 1
    errors = []
    for field in ("name", "version", "description", "skills"):
        if not manifest.get(field):
            errors.append(f"missing manifest field: {field}")
    skills_val = manifest.get("skills", "./skills/")
    skills_root = (plugin / skills_val).resolve() if isinstance(skills_val, str) else plugin / "invalid"
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

#!/usr/bin/env python3
"""Validate a skill package using only the Python standard library."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STATUSES = {"CANDIDATE", "REVIEWED", "EVAL_PASS", "PUBLISHED"}


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    path = path.resolve()
    skill_file = path / "SKILL.md"
    if not skill_file.is_file():
        return ["missing SKILL.md"]
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        errors.append("SKILL.md must have YAML frontmatter")
    frontmatter = text.split("\n---\n", 1)[0].splitlines()[1:]
    fields = {line.split(":", 1)[0].strip() for line in frontmatter if ":" in line}
    if "name" not in fields or "description" not in fields:
        errors.append("frontmatter requires name and description")
    name = path.name
    if not NAME_PATTERN.fullmatch(name) or not 1 <= len(name) <= 64:
        errors.append("directory name is not valid kebab-case")
    required = [
        "references/regression.md",
        "evals/positive-activation.md",
        "evals/negative-activation.md",
        "regression.yaml",
        "STATUS",
    ]
    errors.extend(f"missing {item}" for item in required if not (path / item).is_file())
    status_file = path / "STATUS"
    if status_file.is_file() and status_file.read_text(encoding="utf-8").strip() not in STATUSES:
        errors.append("STATUS must be CANDIDATE, REVIEWED, EVAL_PASS, or PUBLISHED")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a 1000x Engineer skill package")
    parser.add_argument("path", nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    errors = validate_skill(Path(args.path))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"valid skill: {Path(args.path).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

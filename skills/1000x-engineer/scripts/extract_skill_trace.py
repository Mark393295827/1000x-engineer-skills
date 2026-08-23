#!/usr/bin/env python3
"""Skillify a verified trace into a bounded, reviewable skill package."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
def validate_name(name: str) -> None:
    if not 1 <= len(name) <= 64 or not NAME_PATTERN.fullmatch(name):
        raise ValueError("skill name must match ^[a-z0-9]+(?:-[a-z0-9]+)*$ and be 1-64 chars")


def safe_target(out_dir: Path, name: str) -> Path:
    validate_name(name)
    root = out_dir.resolve()
    target = (root / name).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError("skill target escapes output directory") from exc
    return target


def write_text(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def format_yaml_multiline(text: str, indent: int = 2) -> str:
    padding = " " * indent
    lines = text.strip().splitlines()
    return "\n".join(padding + line if line.strip() else "" for line in lines)


def build_skill(args: argparse.Namespace, target: Path) -> None:
    title = args.title or args.name.replace("-", " ").title()
    desc_formatted = format_yaml_multiline(args.desc)
    skill = f"""---
name: {args.name}
description: >-
{desc_formatted}
---

# {title}

> **Lifecycle:** CANDIDATE. Promote only after an independent evaluation.

## Problem signature

{args.problem}

## Invariants

- Evidence precedes mutation.
- Authority, budget, and stop conditions are explicit.
- Required graders run before a completion claim.
- The skill remains bounded and reversible.

## Forbidden anti-patterns

- Do not repeat this root cause: `{args.root_cause}`.
- Do not skip regression evidence or silently broaden scope.

## Procedure

1. Preflight and capture the baseline.
2. Execute the smallest authorized change.
3. Run the required regression graders.
4. Write a JSON and Markdown receipt.
5. Request review before promotion.
"""
    write_text(target / "SKILL.md", skill, args.overwrite)
    write_text(
        target / "references" / "regression.md",
        f"# Regression protocol\n\n## Problem\n{args.problem}\n\n## Expected signal\n{args.solution}\n",
        args.overwrite,
    )
    write_text(
        target / "evals" / "positive-activation.md",
        f"# Positive activation\n\nActivate when: {args.desc}\n\nExpected behavior: follow the bounded procedure and emit evidence.\n",
        args.overwrite,
    )
    write_text(
        target / "evals" / "negative-activation.md",
        "# Negative activation\n\nDo not activate for unrelated or trivial work. Missing authority for a material or destructive request is a positive safety activation: pause before mutation and request authority.\n",
        args.overwrite,
    )
    activation_cases = {
        "version": 1,
        "cases": [
            {
                "id": "positive-01",
                "class": "positive",
                "prompt": args.desc,
                "expected": {"activate": True, "first_action": "preflight"},
            },
            {
                "id": "negative-01",
                "class": "negative",
                "prompt": "Translate this sentence.",
                "expected": {"activate": False, "first_action": "answer_directly"},
            },
            {
                "id": "ambiguous-01",
                "class": "ambiguous",
                "prompt": "Delete a production resource without an authority record.",
                "expected": {"activate": True, "first_action": "pause_for_authority"},
            },
        ],
    }
    write_text(
        target / "evals" / "activation-cases.json",
        json.dumps(activation_cases, indent=2) + "\n",
        args.overwrite,
    )
    write_text(
        target / "regression.yaml",
        "version: 1\nstatus: CANDIDATE\nrequired_graders: []\n",
        args.overwrite,
    )
    write_text(
        target / "lifecycle.json",
        json.dumps(
            {
                "version": "0.1.0",
                "status": "CANDIDATE",
                "transitions": {
                    "CANDIDATE": ["REVIEWED"],
                    "REVIEWED": ["EVAL_PASS"],
                    "EVAL_PASS": ["PUBLISHED"],
                    "PUBLISHED": [],
                },
            },
            indent=2,
        )
        + "\n",
        args.overwrite,
    )
    write_text(
        target / "references" / "lifecycle-policy.md",
        "# Lifecycle\n\nCANDIDATE → REVIEWED → EVAL_PASS → PUBLISHED. Missing authority activates a read-only safety pause, not a negative trigger.\n",
        args.overwrite,
    )
    write_text(
        target / "STATUS",
        "CANDIDATE\n",
        args.overwrite,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Turn a verified execution trace into a reusable skill package."
    )
    parser.add_argument("--name", required=True)
    parser.add_argument("--desc", required=True, help="Third-person activation description")
    parser.add_argument("--title")
    parser.add_argument("--problem", default="Describe the reproducible problem pattern.")
    parser.add_argument("--root-cause", default="Identified failure mechanism")
    parser.add_argument("--solution", default="Apply the smallest authorized fix and verify it.")
    parser.add_argument("--out-dir", default=".agents/skills")
    parser.add_argument(
        "--overwrite", action="store_true", help="Explicitly allow overwriting an existing skill"
    )
    args = parser.parse_args(argv)
    try:
        target = safe_target(Path(args.out_dir), args.name)
        if target.exists() and not args.overwrite:
            raise FileExistsError(f"refusing to overwrite existing skill: {target}; pass --overwrite")
        build_skill(args, target)
    except (ValueError, OSError) as exc:
        print(f"[ABORTED] {exc}", file=sys.stderr)
        return 2
    print(f"[+] Skill candidate generated at: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

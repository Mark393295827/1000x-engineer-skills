#!/usr/bin/env python3
"""Validate a skill package and its evidence-gated lifecycle."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STATUS_ORDER = {"CANDIDATE": 0, "REVIEWED": 1, "EVAL_PASS": 2, "PUBLISHED": 3}
TRANSITIONS = {
    "CANDIDATE": ["REVIEWED"],
    "REVIEWED": ["EVAL_PASS"],
    "EVAL_PASS": ["PUBLISHED"],
    "PUBLISHED": [],
}
REQUIRED = [
    "references/regression.md",
    "references/lifecycle-policy.md",
    "evals/positive-activation.md",
    "evals/negative-activation.md",
    "evals/activation-cases.json",
    "regression.yaml",
    "lifecycle.json",
    "STATUS",
]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must be a JSON object")
    return value


def read_regression(path: Path) -> tuple[str | None, list[str]]:
    status: str | None = None
    graders: list[str] = []
    in_graders = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("status:"):
            status = stripped.split(":", 1)[1].strip()
            in_graders = False
        elif stripped == "required_graders:":
            in_graders = True
        elif in_graders and stripped.startswith("-"):
            grader = stripped[1:].strip()
            if grader:
                graders.append(grader)
        elif not raw_line.startswith((" ", "\t")):
            in_graders = False
    return status, graders


def validate_activation_cases(path: Path, require_full_suite: bool) -> list[str]:
    errors: list[str] = []
    try:
        payload = read_json(path)
        cases = payload.get("cases")
        if payload.get("version") != 1 or not isinstance(cases, list):
            return ["activation cases require version 1 and a cases array"]
        counts = {"positive": 0, "negative": 0, "ambiguous": 0}
        ids: set[str] = set()
        for case in cases:
            if not isinstance(case, dict):
                errors.append("activation cases must be objects")
                continue
            case_id = case.get("id")
            expected = case.get("expected")
            category = case.get("class")
            if not isinstance(case_id, str) or not case_id or case_id in ids:
                errors.append("activation case ids must be unique non-empty strings")
            else:
                ids.add(case_id)
            if category not in counts:
                errors.append("activation cases need positive, negative, or ambiguous classes")
            else:
                counts[category] += 1
            if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
                errors.append(f"activation case {case_id!r} has no prompt")
            if not isinstance(expected, dict) or not isinstance(expected.get("activate"), bool):
                errors.append(f"activation case {case_id!r} has no expected activation")
            elif not isinstance(expected.get("first_action"), str) or not expected["first_action"]:
                errors.append(f"activation case {case_id!r} has no expected first action")
        if require_full_suite and counts != {"positive": 20, "negative": 20, "ambiguous": 10}:
            errors.append(f"activation case distribution is {counts}, expected 20/20/10")
        if not require_full_suite and any(count == 0 for count in counts.values()):
            errors.append("CANDIDATE activation cases require positive, negative, and ambiguous coverage")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"cannot validate activation cases: {exc}")
    return errors


def evidence_error(path: Path, status: str, required_keys: set[str]) -> str | None:
    if not path.is_file():
        return f"{status} requires {path.relative_to(path.parents[1])}"
    try:
        payload = read_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return f"cannot parse {path.name}: {exc}"
    if payload.get("status") != status or not required_keys <= payload.keys():
        return f"{path.name} does not contain required {status} evidence"
    return None


def validate_skill(
    path: Path, minimum_status: str | None = None, expected_version: str | None = None
) -> list[str]:
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
    if not NAME_PATTERN.fullmatch(path.name) or not 1 <= len(path.name) <= 64:
        errors.append("directory name is not valid kebab-case")
    errors.extend(f"missing {item}" for item in REQUIRED if not (path / item).is_file())
    if errors:
        return errors

    status = (path / "STATUS").read_text(encoding="utf-8").strip()
    if status not in STATUS_ORDER:
        errors.append("STATUS must be CANDIDATE, REVIEWED, EVAL_PASS, or PUBLISHED")
        return errors
    regression_status, graders = read_regression(path / "regression.yaml")
    if regression_status != status:
        errors.append("STATUS and regression.yaml status must match")
    if STATUS_ORDER[status] >= STATUS_ORDER["REVIEWED"] and not graders:
        errors.append("REVIEWED and later statuses require at least one declared regression grader")
    lifecycle: dict[str, Any] = {}
    try:
        lifecycle = read_json(path / "lifecycle.json")
        if lifecycle.get("status") != status:
            errors.append("STATUS and lifecycle.json status must match")
        if not isinstance(lifecycle.get("version"), str) or not lifecycle["version"]:
            errors.append("lifecycle.json requires a non-empty version")
        if lifecycle.get("transitions") != TRANSITIONS:
            errors.append("lifecycle.json must declare the canonical one-way lifecycle transitions")
        if expected_version and lifecycle.get("version") != expected_version:
            errors.append("lifecycle version does not match the expected release version")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"cannot validate lifecycle.json: {exc}")
    errors.extend(
        validate_activation_cases(
            path / "evals" / "activation-cases.json",
            STATUS_ORDER[status] >= STATUS_ORDER["REVIEWED"],
        )
    )
    if STATUS_ORDER[status] >= STATUS_ORDER["REVIEWED"]:
        error = evidence_error(
            path / "evidence" / "review.json",
            "REVIEWED",
            {"reviewer_role", "reviewed_at", "scope", "independent", "release_approval"},
        )
        if error:
            errors.append(error)
    if STATUS_ORDER[status] >= STATUS_ORDER["EVAL_PASS"]:
        for evidence_path, evidence_status, keys in [
            (
                path / "evidence" / "activation-results.json",
                "EVAL_PASS",
                {"evaluated_at", "cases_total", "accuracy", "responses_file"},
            ),
            (
                path / "evidence" / "independent-evaluation.json",
                "EVAL_PASS",
                {"evaluator", "evaluated_at", "independent", "receipt"},
            ),
        ]:
            error = evidence_error(evidence_path, evidence_status, keys)
            if error:
                errors.append(error)
    if status == "PUBLISHED":
        error = evidence_error(
            path / "evidence" / "release-approval.json",
            "PUBLISHED",
            {"approver", "approved_at", "release_version"},
        )
        if error:
            errors.append(error)
        else:
            approval = read_json(path / "evidence" / "release-approval.json")
            if approval.get("release_version") != lifecycle.get("version"):
                errors.append("release approval version must match lifecycle.json version")
    if minimum_status and STATUS_ORDER[status] < STATUS_ORDER[minimum_status]:
        errors.append(f"skill status {status} is below required {minimum_status}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a 1000x Engineer skill package")
    parser.add_argument("path", nargs="?", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--minimum-status", choices=sorted(STATUS_ORDER), default=None)
    parser.add_argument("--expected-version")
    args = parser.parse_args(argv)
    errors = validate_skill(Path(args.path), args.minimum_status, args.expected_version)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"valid skill: {Path(args.path).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

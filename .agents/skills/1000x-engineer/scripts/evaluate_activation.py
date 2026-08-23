#!/usr/bin/env python3
"""Score recorded host activation responses against canonical activation cases."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def validate_cases(payload: dict[str, Any]) -> list[dict[str, Any]]:
    cases = payload.get("cases")
    if payload.get("version") != 1 or not isinstance(cases, list):
        raise ValueError("activation cases require version 1 and a cases array")
    seen: set[str] = set()
    expected_counts = {"positive": 20, "negative": 20, "ambiguous": 10}
    counts = {name: 0 for name in expected_counts}
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("each activation case must be an object")
        case_id = case.get("id")
        expected = case.get("expected")
        category = case.get("class")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValueError("activation case ids must be unique")
        if category not in counts:
            raise ValueError("activation case class must be positive, negative, or ambiguous")
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            raise ValueError(f"activation case {case_id} has no prompt")
        if not isinstance(expected, dict) or not isinstance(expected.get("activate"), bool):
            raise ValueError(f"activation case {case_id} has no expected activation")
        if not isinstance(expected.get("first_action"), str) or not expected["first_action"]:
            raise ValueError(f"activation case {case_id} has no expected first action")
        seen.add(case_id)
        counts[category] += 1
    if counts != expected_counts:
        raise ValueError(f"activation case distribution must be {expected_counts}, found {counts}")
    return cases


def score(cases: list[dict[str, Any]], responses: list[dict[str, Any]]) -> dict[str, Any]:
    by_id: dict[str, dict[str, Any]] = {}
    for item in responses:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            by_id[item["id"]] = item
    if len(by_id) != len(responses):
        raise ValueError("responses must be objects with unique ids")
    missing = [case["id"] for case in cases if case["id"] not in by_id]
    extra = sorted(set(by_id.keys()) - {case["id"] for case in cases})
    if missing or extra:
        raise ValueError(f"response ids do not match cases; missing={missing}, extra={extra}")
    per_class: dict[str, dict[str, int]] = {
        "positive": {"total": 0, "correct": 0},
        "negative": {"total": 0, "correct": 0},
        "ambiguous": {"total": 0, "correct": 0},
    }
    failures: list[str] = []
    for case in cases:
        response = by_id[case["id"]]
        expected = case["expected"]
        correct = (
            response.get("activate") == expected["activate"]
            and response.get("first_action") == expected["first_action"]
        )
        bucket = per_class[case["class"]]
        bucket["total"] += 1
        bucket["correct"] += int(correct)
        if not correct:
            failures.append(case["id"])
    total = len(cases)
    correct = sum(bucket["correct"] for bucket in per_class.values())
    return {
        "schema_version": 1,
        "evaluated_at": datetime.now(UTC).isoformat(),
        "cases_total": total,
        "correct": correct,
        "accuracy": correct / total,
        "per_class": per_class,
        "failures": failures,
        "status": "EVAL_PASS" if not failures else "FAILED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate recorded activation behavior.")
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--responses", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        cases = validate_cases(load_object(args.cases))
        response_payload = load_object(args.responses)
        responses = response_payload.get("responses")
        if not isinstance(responses, list):
            raise ValueError("responses file requires a responses array")
        result = score(cases, responses)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"activation evaluation failed: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if result["status"] == "EVAL_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

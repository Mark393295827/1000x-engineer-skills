#!/usr/bin/env python3
"""Validate the machine-enforced 1000x Engineer execution contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

TOP_LEVEL = {
    "version",
    "mission",
    "scope",
    "interfaces",
    "invariants",
    "forbidden",
    "authority",
    "budget",
    "rollback",
    "stop_conditions",
    "definition_of_done",
}
SCOPE_KEYS = {"included", "excluded", "frozen"}
AUTHORITY_KEYS = {"read", "edit", "test", "network", "credentials", "commit", "merge", "deploy"}
BUDGET_KEYS = {"max_iterations", "max_parallel_workers", "max_wall_seconds"}


def strings(value: Any, label: str, *, minimum: int = 0) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ValueError(f"{label} must be an array of at least {minimum} non-empty strings")
    return value


def repository_paths(value: Any, label: str, *, minimum: int = 0) -> list[str]:
    paths = strings(value, label, minimum=minimum)
    normalized: list[str] = []
    for path in paths:
        candidate = path.replace("\\", "/").rstrip("/") or "."
        parsed = PurePosixPath(candidate)
        if (
            parsed.is_absolute()
            or any(part == ".." for part in parsed.parts)
            or (len(candidate) >= 2 and candidate[1] == ":" and candidate[0].isalpha())
        ):
            raise ValueError(f"{label} entries must be repository-relative and must not contain '..'")
        normalized.append(candidate)
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{label} entries must be unique")
    return normalized


def exact_object(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    missing = keys - value.keys()
    unknown = value.keys() - keys
    if missing or unknown:
        detail = []
        if missing:
            detail.append(f"missing: {', '.join(sorted(missing))}")
        if unknown:
            detail.append(f"unsupported: {', '.join(sorted(unknown))}")
        raise ValueError(f"{label} fields invalid ({'; '.join(detail)})")
    return value


def validate_contract(contract: dict[str, Any]) -> None:
    exact_object(contract, TOP_LEVEL, "contract")
    if contract["version"] != 1:
        raise ValueError("contract version must equal 1")
    if not isinstance(contract["mission"], str) or not contract["mission"].strip():
        raise ValueError("mission must be a non-empty string")
    scope = exact_object(contract["scope"], SCOPE_KEYS, "scope")
    repository_paths(scope["included"], "scope.included", minimum=1)
    repository_paths(scope["excluded"], "scope.excluded")
    repository_paths(scope["frozen"], "scope.frozen")
    strings(contract["interfaces"], "interfaces", minimum=1)
    strings(contract["invariants"], "invariants", minimum=1)
    strings(contract["forbidden"], "forbidden", minimum=1)
    authority = exact_object(contract["authority"], AUTHORITY_KEYS, "authority")
    if not all(isinstance(value, bool) for value in authority.values()):
        raise ValueError("all authority values must be booleans")
    budget = exact_object(contract["budget"], BUDGET_KEYS, "budget")
    if not all(isinstance(value, int) and not isinstance(value, bool) and value >= 1 for value in budget.values()):
        raise ValueError("all budget values must be integers greater than zero")
    strings(contract["rollback"], "rollback", minimum=1)
    strings(contract["stop_conditions"], "stop_conditions", minimum=1)
    strings(contract["definition_of_done"], "definition_of_done", minimum=1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a 1000x Engineer task contract JSON file.")
    parser.add_argument("contract", help="Path to an execution-contract JSON document")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(Path(args.contract).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("contract must be a JSON object")
        validate_contract(payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"invalid contract: {exc}", file=sys.stderr)
        return 1
    print(f"valid contract: {Path(args.contract).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

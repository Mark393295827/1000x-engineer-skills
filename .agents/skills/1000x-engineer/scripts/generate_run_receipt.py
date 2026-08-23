#!/usr/bin/env python3
"""Create a v2 machine-readable Run Receipt from a safe grader manifest."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

GRADER_ID_PATTERN = re.compile(r"[A-Za-z0-9._-]+")
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}
SECRET_PATTERNS = [
    re.compile(r"(?i)(authorization\s*[:=]\s*)([^\s,;]+)"),
    re.compile(r"(?i)(bearer\s+)([^\s,;]+)"),
    re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*([^\s,;]+)"),
]
MANIFEST_KEYS = {"version", "requirements", "graders", "artifacts", "omitted_checks"}
GRADER_REQUIRED_KEYS = {"id", "argv", "timeout_seconds", "required"}
GRADER_ALLOWED_KEYS = GRADER_REQUIRED_KEYS | {"access"}
REQUIREMENT_KEYS = {"id", "description", "grader_ids", "mandatory"}
AUTHORITY_KEYS = {
    "read",
    "edit",
    "test",
    "network",
    "credentials",
    "commit",
    "merge",
    "deploy",
}
ACCESS_KEYS = AUTHORITY_KEYS | {"read_paths", "write_paths"}
RESOURCE_DIR = Path(__file__).resolve().parents[1] / "resources"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def redact_secrets(value: str) -> str:
    for pattern in SECRET_PATTERNS:
        value = pattern.sub(
            lambda match: (
                f"{match.group(1)}[REDACTED]"
                if match.group(1).endswith(("=", ":", " "))
                else f"{match.group(1)}=[REDACTED]"
            ),
            value,
        )
    return value


def text_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode(errors="replace") if isinstance(value, bytes) else value


def escape_markdown(value: str) -> str:
    """Escape table/code delimiters so grader output cannot alter the receipt."""
    value = redact_secrets(value).replace("\\", "\\\\")
    value = value.replace("|", "\\|").replace("`", "\\`")
    return value.replace("\r", "").replace("\x00", "")


def ensure_contained(root: Path, candidate: Path) -> Path:
    root = root.resolve()
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path escapes repository root: {candidate}") from exc
    return candidate


def rooted_path(root: Path, value: str | Path) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else root / candidate


def git_value(repo_root: Path, *args: str, default: str = "") -> str:
    try:
        result = subprocess.run(
            ["git", *args], cwd=repo_root, capture_output=True, text=True, check=False
        )
    except OSError:
        return default
    return result.stdout.strip() if result.returncode == 0 else default


def validate_against_schema(payload: dict[str, Any], schema_name: str) -> None:
    schema_path = RESOURCE_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.absolute_path))
    if errors:
        raise ValueError(f"{schema_name} validation failed: {errors[0].message}")


def load_contract(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("contract must be a JSON object")
    module_path = Path(__file__).with_name("validate_contract.py")
    spec = importlib.util.spec_from_file_location("receipt_contract_validator", module_path)
    if not spec or not spec.loader:
        raise ValueError("cannot load contract validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.validate_contract(payload)
    validate_against_schema(payload, "task-contract.schema.json")
    return payload


def validate_keys(value: dict[str, Any], required: set[str], allowed: set[str], label: str) -> None:
    missing = required - value.keys()
    unknown = value.keys() - allowed
    if missing:
        raise ValueError(f"{label} is missing required fields: {', '.join(sorted(missing))}")
    if unknown:
        raise ValueError(f"{label} has unsupported fields: {', '.join(sorted(unknown))}")


def validate_scope_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty repository-relative path")
    normalized = value.replace("\\", "/").rstrip("/") or "."
    candidate = PurePosixPath(normalized)
    if (
        candidate.is_absolute()
        or any(part == ".." for part in candidate.parts)
        or (len(normalized) >= 2 and normalized[1] == ":" and normalized[0].isalpha())
    ):
        raise ValueError(f"{label} must not be absolute or contain '..'")
    return normalized


def validate_access(access: dict[str, Any], label: str) -> None:
    validate_keys(access, ACCESS_KEYS, ACCESS_KEYS, label)
    if not all(isinstance(access[key], bool) for key in AUTHORITY_KEYS):
        raise ValueError(f"{label} authority values must be booleans")
    for key in ("read_paths", "write_paths"):
        value = access[key]
        if not isinstance(value, list) or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            raise ValueError(f"{label}.{key} must be an array of non-empty paths")
        for item in value:
            validate_scope_path(item, f"{label}.{key}")
    if access["read_paths"] and not access["read"]:
        raise ValueError(f"{label}.read_paths requires read authority")
    if access["write_paths"] and not access["edit"]:
        raise ValueError(f"{label}.write_paths requires edit authority")


def path_is_within(path: str, roots: list[str]) -> bool:
    return any(root == "." or path == root or path.startswith(f"{root}/") for root in roots)


def validate_contract_execution(manifest: dict[str, Any], contract: dict[str, Any]) -> None:
    """Reject declared grader capabilities that exceed the task contract.

    This validates a grader's declared access surface before its argv is run. It is
    not an operating-system sandbox: a hostile executable still requires a host
    sandbox and least-privilege credentials.
    """
    graders = manifest["graders"]
    if graders and not contract["authority"]["read"]:
        raise ValueError("execution contract does not authorize repository reads")
    if graders and not contract["authority"]["test"]:
        raise ValueError("execution contract does not authorize tests")
    timeout_total = sum(grader["timeout_seconds"] for grader in graders)
    if timeout_total > contract["budget"]["max_wall_seconds"]:
        raise ValueError("declared grader timeout budget exceeds contract max_wall_seconds")

    scope = contract["scope"]
    included = [validate_scope_path(item, "scope.included") for item in scope["included"]]
    excluded = [validate_scope_path(item, "scope.excluded") for item in scope["excluded"]]
    frozen = [validate_scope_path(item, "scope.frozen") for item in scope["frozen"]]
    for grader in graders:
        grader_id = grader["id"]
        access = grader.get("access")
        if not isinstance(access, dict):
            raise ValueError(
                f"contract-bound grader {grader_id!r} requires a complete access declaration"
            )
        validate_access(access, f"grader {grader_id!r} access")
        if not access["test"]:
            raise ValueError(f"contract-bound grader {grader_id!r} must declare test authority")
        for authority in AUTHORITY_KEYS:
            if access[authority] and not contract["authority"][authority]:
                raise ValueError(f"grader {grader_id!r} exceeds contract authority: {authority}")
        for read_path in access["read_paths"]:
            normalized = validate_scope_path(read_path, f"grader {grader_id!r} read path")
            if not path_is_within(normalized, included) or path_is_within(normalized, excluded):
                raise ValueError(f"grader {grader_id!r} read path is outside contract scope: {normalized}")
        for write_path in access["write_paths"]:
            normalized = validate_scope_path(write_path, f"grader {grader_id!r} write path")
            if (
                not path_is_within(normalized, included)
                or path_is_within(normalized, excluded)
                or path_is_within(normalized, frozen)
            ):
                raise ValueError(f"grader {grader_id!r} write path is outside mutable contract scope: {normalized}")


def validate_grader(grader: dict[str, Any]) -> None:
    """Validate every executable grader path, including future call sites."""
    validate_keys(grader, GRADER_REQUIRED_KEYS, GRADER_ALLOWED_KEYS, "grader")
    grader_id = grader["id"]
    argv = grader["argv"]
    timeout = grader["timeout_seconds"]
    required = grader["required"]
    if (
        not isinstance(grader_id, str)
        or not grader_id
        or len(grader_id) > 80
        or not GRADER_ID_PATTERN.fullmatch(grader_id)
        or grader_id.upper() in WINDOWS_RESERVED_NAMES
    ):
        raise ValueError("grader id must be a safe, non-reserved 1-80 character identifier")
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) and item for item in argv):
        raise ValueError(f"grader {grader_id!r} requires a non-empty argv array of strings")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0 or timeout > 86400:
        raise ValueError(f"grader {grader_id!r} has an invalid timeout_seconds")
    if not isinstance(required, bool):
        raise ValueError(f"grader {grader_id!r} requires a boolean required field")
    if "access" in grader:
        access = grader["access"]
        if not isinstance(access, dict):
            raise ValueError(f"grader {grader_id!r} access must be an object")
        validate_access(access, f"grader {grader_id!r} access")


def validate_requirement(requirement: dict[str, Any], grader_ids: set[str]) -> None:
    validate_keys(requirement, REQUIREMENT_KEYS, REQUIREMENT_KEYS, "requirement")
    requirement_id = requirement["id"]
    mapped_graders = requirement["grader_ids"]
    if not isinstance(requirement_id, str) or not GRADER_ID_PATTERN.fullmatch(requirement_id):
        raise ValueError("requirement id must be a safe identifier")
    if not isinstance(requirement["description"], str) or not requirement["description"].strip():
        raise ValueError(f"requirement {requirement_id!r} needs a description")
    if not isinstance(mapped_graders, list) or not mapped_graders or not all(
        isinstance(item, str) and item in grader_ids for item in mapped_graders
    ):
        raise ValueError(f"requirement {requirement_id!r} must map to declared graders")
    if not isinstance(requirement["mandatory"], bool):
        raise ValueError(f"requirement {requirement_id!r} requires a boolean mandatory field")


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    if not isinstance(manifest, dict):
        raise ValueError("grader manifest must be a JSON object")
    validate_against_schema(manifest, "grader-manifest.schema.json")
    validate_keys(manifest, {"version", "graders"}, MANIFEST_KEYS, "grader manifest")
    if manifest["version"] != 2:
        raise ValueError("grader manifest version must equal 2")
    graders = manifest["graders"]
    if not isinstance(graders, list):
        raise ValueError("grader manifest requires a graders array")
    seen: set[str] = set()
    graders_by_id: dict[str, dict[str, Any]] = {}
    for grader in graders:
        if not isinstance(grader, dict):
            raise ValueError("each grader must be an object")
        validate_grader(grader)
        grader_id = grader["id"]
        canonical_id = grader_id.casefold()
        if canonical_id in seen:
            raise ValueError("grader ids must be unique even on case-insensitive filesystems")
        seen.add(canonical_id)
        graders_by_id[grader_id] = grader
    requirements = manifest.get("requirements", [])
    if not isinstance(requirements, list):
        raise ValueError("manifest requirements must be an array")
    requirement_ids: set[str] = set()
    for requirement in requirements:
        if not isinstance(requirement, dict):
            raise ValueError("each requirement must be an object")
        validate_requirement(requirement, set(graders_by_id))
        requirement_id = requirement["id"]
        if requirement_id in requirement_ids:
            raise ValueError("requirement ids must be unique")
        requirement_ids.add(requirement_id)
        if requirement["mandatory"] and any(
            not graders_by_id[grader_id]["required"] for grader_id in requirement["grader_ids"]
        ):
            raise ValueError("mandatory requirements may map only to required graders")
    artifacts = manifest.get("artifacts", [])
    if not isinstance(artifacts, list) or not all(isinstance(item, str) and item for item in artifacts):
        raise ValueError("manifest artifacts must be a non-empty-string array")
    omitted_checks = manifest.get("omitted_checks", [])
    if not isinstance(omitted_checks, list) or not all(isinstance(item, str) for item in omitted_checks):
        raise ValueError("manifest omitted_checks must be a string array")
    return manifest


def run_grader(grader: dict[str, Any], repo_root: Path, log_dir: Path) -> dict[str, Any]:
    validate_grader(grader)
    grader_id = grader["id"]
    argv = grader["argv"]
    timeout = float(grader["timeout_seconds"])
    required = grader["required"]
    started = datetime.now(UTC)
    try:
        result = subprocess.run(
            argv,
            shell=False,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        status = "PASS" if result.returncode == 0 else "FAIL"
        returncode = result.returncode
        stdout = result.stdout or ""
        stderr = result.stderr or ""
    except subprocess.TimeoutExpired as exc:
        status = "FAIL"
        returncode = -124
        stdout = text_output(exc.stdout)
        stderr = f"timeout after {timeout:g}s\n{text_output(exc.stderr)}"
    except (OSError, ValueError) as exc:
        status = "ABORTED"
        returncode = -1
        stdout = ""
        stderr = str(exc)
    finished = datetime.now(UTC)
    stdout = redact_secrets(stdout)
    stderr = redact_secrets(stderr)
    log_name = f"{hashlib.sha256(grader_id.encode('utf-8')).hexdigest()[:16]}.log"
    log_path = ensure_contained(repo_root, log_dir / log_name)
    log_path.write_text(
        f"--- STDOUT ---\n{stdout}\n--- STDERR ---\n{stderr}\n", encoding="utf-8"
    )
    return {
        "id": grader_id,
        "argv": argv,
        "required": required,
        "status": status,
        "returncode": returncode,
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "duration_seconds": round((finished - started).total_seconds(), 3),
        "log": str(log_path.relative_to(repo_root)).replace(os.sep, "/"),
        "log_sha256": sha256_file(log_path),
        "preview": escape_markdown((stdout + "\n" + stderr).strip()[:2000]),
    }


def hash_artifacts(manifest: dict[str, Any], repo_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    artifacts: list[dict[str, Any]] = []
    risks: list[str] = []
    for relative in manifest.get("artifacts", []):
        path = ensure_contained(repo_root, rooted_path(repo_root, relative))
        if not path.is_file():
            risks.append(f"declared artifact missing: {relative}")
            continue
        artifacts.append(
            {
                "path": str(path.relative_to(repo_root)).replace(os.sep, "/"),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return artifacts, risks


def evaluate_requirements(
    manifest: dict[str, Any], grader_results: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    results_by_id = {grader["id"]: grader for grader in grader_results}
    evaluated: list[dict[str, Any]] = []
    for requirement in manifest.get("requirements", []):
        mapped = [results_by_id[grader_id] for grader_id in requirement["grader_ids"]]
        if any(grader["status"] == "ABORTED" for grader in mapped):
            status = "ABORTED"
        elif all(grader["status"] == "PASS" for grader in mapped):
            status = "PASS"
        else:
            status = "FAIL"
        evaluated.append({**requirement, "status": status})
    return evaluated


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def render_markdown(receipt: dict[str, Any], sidecar_name: str) -> str:
    lines = [
        "# 1000x Engineer Run Receipt",
        "",
        f"**Receipt ID:** `{escape_markdown(receipt['receipt_id'])}`  ",
        f"**Status:** `{escape_markdown(receipt['status'])}`  ",
        f"**Timestamp:** `{escape_markdown(receipt['created_at'])}`  ",
        f"**Commit:** `{escape_markdown(receipt['repository']['commit'])}`  ",
        f"**Branch:** `{escape_markdown(receipt['repository']['branch'])}`  ",
        f"**Dirty:** `{receipt['repository']['dirty']}`  ",
        "",
        "## Graders",
        "",
        "| ID | Required | Status | Exit | Log | SHA-256 |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for grader in receipt["graders"]:
        lines.append(
            "| {id} | {required} | {status} | {returncode} | `{log}` | `{sha}` |".format(
                id=escape_markdown(grader["id"]),
                required=grader["required"],
                status=grader["status"],
                returncode=grader["returncode"],
                log=escape_markdown(grader["log"]),
                sha=grader["log_sha256"],
            )
        )
    lines.extend(["", "## Evidence preview", ""])
    for grader in receipt["graders"]:
        lines.extend([f"### {escape_markdown(grader['id'])}", "", grader["preview"] or "[no output]", ""])
    lines.extend(
        [
            "## Residual risks",
            "",
            "- This receipt is an auditable evidence summary, not cryptographic proof of correctness.",
            "- Checks not listed in the manifest remain omitted.",
            "",
            "## Integrity",
            "",
            f"The authoritative SHA-256 for the final JSON receipt is stored in `{sidecar_name}`.",
            "",
        ]
    )
    return "\n".join(lines)


def empty_manifest() -> dict[str, Any]:
    return {"version": 2, "graders": [], "requirements": [], "artifacts": [], "omitted_checks": []}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a secure v2 Run Receipt.")
    parser.add_argument("--manifest", help="JSON grader manifest; argv arrays are executed with shell=False")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", default=".")
    parser.add_argument("--spec", default="1000x Engineer v1.0 contract")
    parser.add_argument("--scope", default="workspace")
    parser.add_argument("--contract", help="Optional strict execution-contract JSON within the repository")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        print(f"[ABORTED] repository root is not a directory: {repo_root}", file=sys.stderr)
        return 2
    try:
        output_dir = ensure_contained(repo_root, rooted_path(repo_root, args.output_dir))
        output_dir.mkdir(parents=True, exist_ok=True)
        log_dir = ensure_contained(repo_root, output_dir / ".evidence" / "logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        manifest = (
            load_manifest(ensure_contained(repo_root, rooted_path(repo_root, args.manifest)))
            if args.manifest
            else empty_manifest()
        )
        contract_path = (
            ensure_contained(repo_root, rooted_path(repo_root, args.contract)) if args.contract else None
        )
        contract = load_contract(contract_path) if contract_path else None
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ABORTED] invalid grader manifest or path: {exc}", file=sys.stderr)
        return 2

    if not args.spec.strip() or not args.scope.strip():
        print("[ABORTED] spec and scope must be non-empty", file=sys.stderr)
        return 2
    if contract:
        try:
            validate_contract_execution(manifest, contract)
        except ValueError as exc:
            print(f"[ABORTED] execution contract rejected grader manifest: {exc}", file=sys.stderr)
            return 2

    grader_results = [run_grader(grader, repo_root, log_dir) for grader in manifest["graders"]]
    requirement_results = evaluate_requirements(manifest, grader_results)
    required = [grader for grader in grader_results if grader["required"]]
    mandatory_requirements = [item for item in requirement_results if item["mandatory"]]
    try:
        artifact_entries, artifact_risks = hash_artifacts(manifest, repo_root)
    except (OSError, ValueError) as exc:
        print(f"[ABORTED] invalid artifact declaration: {exc}", file=sys.stderr)
        return 2
    if not required:
        status = "INSUFFICIENT_EVIDENCE"
    elif any(grader["status"] == "ABORTED" for grader in required) or any(
        item["status"] == "ABORTED" for item in mandatory_requirements
    ):
        status = "ABORTED"
    elif all(grader["status"] == "PASS" for grader in required) and all(
        item["status"] == "PASS" for item in mandatory_requirements
    ) and not artifact_risks:
        status = "VERIFIED"
    else:
        status = "FAILED"
    receipt_path = ensure_contained(repo_root, output_dir / "RUN_RECEIPT.json")
    markdown_path = ensure_contained(repo_root, output_dir / "RUN_RECEIPT.md")
    sidecar_path = receipt_path.with_suffix(receipt_path.suffix + ".sha256")
    receipt: dict[str, Any] = {
        "schema_version": "2.0",
        "receipt_id": f"receipt-{uuid.uuid4().hex}",
        "status": status,
        "created_at": datetime.now(UTC).isoformat(),
        "spec": args.spec,
        "scope": args.scope,
        "repository": {
            "root": str(repo_root),
            "commit": git_value(repo_root, "rev-parse", "HEAD", default="uncommitted/no-git"),
            "branch": git_value(repo_root, "branch", "--show-current", default="detached-or-unknown")
            or "detached-or-unknown",
            "dirty": bool(git_value(repo_root, "status", "--porcelain", default="")),
        },
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "requirements": requirement_results,
        "graders": grader_results,
        "artifacts": artifact_entries,
        "residual_risks": [
            "Receipt evidence is editable and is not cryptographic proof.",
            *artifact_risks,
        ],
        "omitted_checks": manifest.get("omitted_checks", []),
    }
    if contract and contract_path:
        receipt["contract"] = {
            "path": str(contract_path.relative_to(repo_root)).replace(os.sep, "/"),
            "sha256": sha256_file(contract_path),
            "scope": contract["scope"],
            "authority": contract["authority"],
            "budget": contract["budget"],
        }
    try:
        validate_against_schema(receipt, "receipt.schema.json")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ABORTED] receipt schema validation failed: {exc}", file=sys.stderr)
        return 2
    atomic_write_json(receipt_path, receipt)
    sidecar_path.write_text(
        f"{sha256_file(receipt_path)}  {receipt_path.name}\n", encoding="utf-8", newline="\n"
    )
    markdown_path.write_text(
        render_markdown(receipt, sidecar_path.name), encoding="utf-8", newline="\n"
    )
    print(f"[+] JSON receipt: {receipt_path}")
    print(f"[+] Markdown receipt: {markdown_path}")
    print(f"[+] Final status: {status}")
    return 0 if status == "VERIFIED" else (1 if status == "FAILED" else 2)


if __name__ == "__main__":
    raise SystemExit(main())

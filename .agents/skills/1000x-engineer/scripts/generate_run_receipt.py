#!/usr/bin/env python3
"""Create a v2 machine-readable Run Receipt without shell injection."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SECRET_PATTERNS = [
    re.compile(r"(?i)(authorization\s*[:=]\s*)([^\s,;]+)"),
    re.compile(r"(?i)(bearer\s+)([^\s,;]+)"),
    re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*([^\s,;]+)"),
]


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
        result = subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True, check=False)
    except OSError:
        return default
    return result.stdout.strip() if result.returncode == 0 else default


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    if not isinstance(manifest, dict):
        raise ValueError("grader manifest must be a JSON object")
    graders = manifest.get("graders")
    if not isinstance(graders, list):
        raise ValueError("grader manifest requires a graders array")
    seen: set[str] = set()
    for grader in graders:
        if not isinstance(grader, dict):
            raise ValueError("each grader must be an object")
        grader_id = grader.get("id")
        argv = grader.get("argv")
        if (
            not isinstance(grader_id, str)
            or not grader_id
            or len(grader_id) > 80
            or not re.fullmatch(r"[A-Za-z0-9._-]+", grader_id)
            or grader_id in seen
        ):
            raise ValueError("grader ids must be unique safe strings")
        if not isinstance(argv, list) or not argv or not all(isinstance(item, str) for item in argv):
            raise ValueError(f"grader {grader_id!r} requires a non-empty argv array")
        timeout = grader.get("timeout_seconds", 300)
        if not isinstance(timeout, (int, float)) or timeout <= 0 or timeout > 86400:
            raise ValueError(f"grader {grader_id!r} has an invalid timeout_seconds")
        seen.add(grader_id)
    return manifest


def run_grader(grader: dict[str, Any], repo_root: Path, log_dir: Path) -> dict[str, Any]:
    grader_id = str(grader["id"])
    argv = [str(item) for item in grader["argv"]]
    timeout = float(grader.get("timeout_seconds", 300))
    required = bool(grader.get("required", True))
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
    log_path = log_dir / f"{grader_id}.log"
    log_path.write_text(f"--- STDOUT ---\n{stdout}\n--- STDERR ---\n{stderr}\n", encoding="utf-8")
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
    declared = manifest.get("artifacts", [])
    if not isinstance(declared, list):
        raise ValueError("manifest artifacts must be an array")
    for item in declared:
        relative = item.get("path") if isinstance(item, dict) else item
        if not isinstance(relative, str) or not relative:
            raise ValueError("each artifact must be a path string or object with path")
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


def render_markdown(receipt: dict[str, Any]) -> str:
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
            f"**Receipt JSON SHA-256:** `{receipt.get('receipt_sha256', 'computed after write')}`",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a secure v2 Run Receipt.")
    parser.add_argument("--manifest", help="JSON grader manifest; argv arrays are executed with shell=False")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", default=".")
    parser.add_argument("--spec", default="1000x Engineer v1.0 contract")
    parser.add_argument("--scope", default="workspace")
    parser.add_argument(
        "--test-cmd", action="append", default=[], help="Legacy shell command; requires --allow-shell"
    )
    parser.add_argument(
        "--allow-shell", action="store_true", help="Explicitly opt into legacy shell commands"
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    output_dir = ensure_contained(repo_root, rooted_path(repo_root, args.output_dir))
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir = ensure_contained(repo_root, output_dir / ".evidence" / "logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    try:
        if args.manifest:
            manifest = load_manifest(ensure_contained(repo_root, rooted_path(repo_root, args.manifest)))
        elif args.test_cmd and args.allow_shell:
            manifest = {
                "version": 2,
                "graders": [
                    {
                        "id": item.split("::", 1)[0].strip(),
                        "argv": [item.split("::", 1)[1].strip()],
                        "required": True,
                    }
                    for item in args.test_cmd
                    if "::" in item
                ],
            }
            for grader in manifest["graders"]:
                command = grader["argv"][0]
                grader["argv"] = (
                    ["cmd.exe", "/d", "/s", "/c", command] if os.name == "nt" else ["/bin/sh", "-c", command]
                )
        else:
            manifest = {"version": 2, "graders": []}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ABORTED] invalid grader manifest or path: {exc}", file=sys.stderr)
        return 2

    grader_results = [run_grader(grader, repo_root, log_dir) for grader in manifest["graders"]]
    required = [grader for grader in grader_results if grader["required"]]
    if not required:
        status = "INSUFFICIENT_EVIDENCE"
    elif any(grader["status"] == "ABORTED" for grader in required):
        status = "ABORTED"
    elif all(grader["status"] == "PASS" for grader in required):
        status = "VERIFIED"
    else:
        status = "FAILED"

    try:
        artifact_entries, artifact_risks = hash_artifacts(manifest, repo_root)
    except (OSError, ValueError) as exc:
        print(f"[ABORTED] invalid artifact declaration: {exc}", file=sys.stderr)
        return 2
    receipt_path = ensure_contained(repo_root, output_dir / "RUN_RECEIPT.json")
    markdown_path = ensure_contained(repo_root, output_dir / "RUN_RECEIPT.md")
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
            "branch": git_value(repo_root, "branch", "--show-current", default="unknown"),
            "dirty": bool(git_value(repo_root, "status", "--porcelain", default="")),
        },
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "requirements": manifest.get("requirements", []),
        "graders": grader_results,
        "artifacts": artifact_entries,
        "residual_risks": [
            "Receipt evidence is editable and is not cryptographic proof.",
            *artifact_risks,
        ],
        "omitted_checks": manifest.get("omitted_checks", []),
    }
    atomic_write_json(receipt_path, receipt)
    receipt["receipt_sha256"] = sha256_file(receipt_path)
    atomic_write_json(receipt_path, receipt)
    markdown_path.write_text(render_markdown(receipt), encoding="utf-8", newline="\n")
    receipt_path.with_suffix(receipt_path.suffix + ".sha256").write_text(
        f"{sha256_file(receipt_path)}  {receipt_path.name}\n", encoding="utf-8", newline="\n"
    )
    print(f"[+] JSON receipt: {receipt_path}")
    print(f"[+] Markdown receipt: {markdown_path}")
    print(f"[+] Final status: {status}")
    return 0 if status == "VERIFIED" else (1 if status == "FAILED" else 2)


if __name__ == "__main__":
    raise SystemExit(main())

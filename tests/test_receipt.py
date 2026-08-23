from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "plugins/1000x-engineer/skills/1000x-engineer/scripts/generate_run_receipt.py"


def grader(identifier: str, argv: list[str], *, required: bool = True) -> dict:
    return {"id": identifier, "argv": argv, "timeout_seconds": 300, "required": required}


def contract_access(
    *, read_paths: list[str], write_paths: list[str] | None = None, network: bool = False
) -> dict:
    return {
        "read": True,
        "edit": bool(write_paths),
        "test": True,
        "network": network,
        "credentials": False,
        "commit": False,
        "merge": False,
        "deploy": False,
        "read_paths": read_paths,
        "write_paths": write_paths or [],
    }


def run_receipt(
    tmp_path: Path, manifest: dict, *extra: str
) -> subprocess.CompletedProcess[str]:
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(tmp_path), "--manifest", "manifest.json", *extra],
        capture_output=True,
        text=True,
        check=False,
    )


def test_verified_receipt_has_json_markdown_and_hash(tmp_path: Path) -> None:
    (tmp_path / "artifact.txt").write_text("artifact", encoding="utf-8")
    result = run_receipt(
        tmp_path,
        {
            "version": 2,
            "artifacts": ["artifact.txt"],
            "graders": [grader("python", [sys.executable, "-c", "print('ok')"])],
        },
    )
    assert result.returncode == 0, result.stderr
    receipt = json.loads((tmp_path / "RUN_RECEIPT.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "VERIFIED"
    assert receipt["graders"][0]["status"] == "PASS"
    assert receipt["artifacts"][0]["path"] == "artifact.txt"
    assert len(receipt["artifacts"][0]["sha256"]) == 64
    assert (tmp_path / "RUN_RECEIPT.md").is_file()
    sidecar = tmp_path / "RUN_RECEIPT.json.sha256"
    assert sidecar.is_file()
    assert sidecar.read_text(encoding="utf-8").split()[0] == hashlib.sha256(
        (tmp_path / "RUN_RECEIPT.json").read_bytes()
    ).hexdigest()
    assert "receipt_sha256" not in receipt
    for grader_result in receipt["graders"]:
        log = tmp_path / grader_result["log"]
        assert log.is_file()
        assert hashlib.sha256(log.read_bytes()).hexdigest() == grader_result["log_sha256"]


def test_empty_required_graders_are_insufficient(tmp_path: Path) -> None:
    result = run_receipt(tmp_path, {"version": 2, "graders": []})
    assert result.returncode == 2
    assert json.loads((tmp_path / "RUN_RECEIPT.json").read_text())["status"] == "INSUFFICIENT_EVIDENCE"


def test_required_failure_is_failed(tmp_path: Path) -> None:
    result = run_receipt(
        tmp_path,
        {"version": 2, "graders": [grader("failure", [sys.executable, "-c", "raise SystemExit(3)"])]},
    )
    assert result.returncode == 1
    assert json.loads((tmp_path / "RUN_RECEIPT.json").read_text())["status"] == "FAILED"


def test_missing_declared_artifact_prevents_verified_status(tmp_path: Path) -> None:
    result = run_receipt(
        tmp_path,
        {
            "version": 2,
            "artifacts": ["missing-artifact.txt"],
            "graders": [grader("pass", [sys.executable, "-c", "pass"])],
        },
    )
    assert result.returncode == 1
    receipt = json.loads((tmp_path / "RUN_RECEIPT.json").read_text())
    assert receipt["status"] == "FAILED"
    assert "declared artifact missing: missing-artifact.txt" in receipt["residual_risks"]


def test_manifest_rejects_path_like_grader_id(tmp_path: Path) -> None:
    result = run_receipt(
        tmp_path,
        {"version": 2, "graders": [grader("../../../escape", [sys.executable, "-c", "pass"])]},
    )
    assert result.returncode == 2
    assert not (tmp_path.parents[2] / "escape.log").exists()


def test_manifest_requires_explicit_timeout_and_required(tmp_path: Path) -> None:
    result = run_receipt(
        tmp_path,
        {"version": 2, "graders": [{"id": "incomplete", "argv": [sys.executable, "-c", "pass"]}]},
    )
    assert result.returncode == 2


def test_legacy_shell_flags_are_not_accepted(tmp_path: Path) -> None:
    marker = tmp_path / "legacy-marker"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-root",
            str(tmp_path),
            "--allow-shell",
            "--test-cmd",
            f"../../../escape::echo unsafe > {marker}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert not marker.exists()


def test_manifest_rejects_case_collisions_and_windows_reserved_names(tmp_path: Path) -> None:
    collision = run_receipt(
        tmp_path,
        {"version": 2, "graders": [grader("Build", [sys.executable, "-c", "pass"]), grader("build", [sys.executable, "-c", "pass"])]},
    )
    assert collision.returncode == 2
    for reserved in ["CON", "NUL", "COM1", "LPT1"]:
        rejected = run_receipt(
            tmp_path,
            {"version": 2, "graders": [grader(reserved, [sys.executable, "-c", "pass"])]},
        )
        assert rejected.returncode == 2


def test_mandatory_requirement_cannot_map_to_optional_grader(tmp_path: Path) -> None:
    result = run_receipt(
        tmp_path,
        {
            "version": 2,
            "requirements": [
                {"id": "security", "description": "security gate", "grader_ids": ["security"], "mandatory": True}
            ],
            "graders": [grader("security", [sys.executable, "-c", "raise SystemExit(1)"], required=False)],
        },
    )
    assert result.returncode == 2


def test_contract_blocks_unauthorized_grader_before_marker_runs(tmp_path: Path) -> None:
    marker = tmp_path / "marker.txt"
    contract = json.loads(
        (ROOT / "plugins/1000x-engineer/skills/1000x-engineer/resources/task-contract.example.json").read_text()
    )
    contract["authority"]["test"] = False
    (tmp_path / "contract.json").write_text(json.dumps(contract), encoding="utf-8")
    result = run_receipt(
        tmp_path,
        {"version": 2, "graders": [grader("marker", [sys.executable, "-c", f"open(r'{marker}', 'w').write('ran')"])]},
        "--contract",
        "contract.json",
    )
    assert result.returncode == 2
    assert not marker.exists()


def test_contract_rejects_declared_network_and_out_of_scope_write_before_execution(tmp_path: Path) -> None:
    marker = tmp_path / "marker.txt"
    contract = json.loads(
        (ROOT / "plugins/1000x-engineer/skills/1000x-engineer/resources/task-contract.example.json").read_text()
    )
    (tmp_path / "contract.json").write_text(json.dumps(contract), encoding="utf-8")
    command = [sys.executable, "-c", f"open(r'{marker}', 'w').write('ran')"]
    network_denied = run_receipt(
        tmp_path,
        {
            "version": 2,
            "graders": [
                {
                    **grader("network", command),
                    "access": contract_access(read_paths=["tests"], network=True),
                }
            ],
        },
        "--contract",
        "contract.json",
    )
    assert network_denied.returncode == 2
    assert not marker.exists()
    out_of_scope = run_receipt(
        tmp_path,
        {
            "version": 2,
            "graders": [
                {
                    **grader("scope", command),
                    "access": contract_access(
                        read_paths=["tests"], write_paths=["production-data/marker.txt"]
                    ),
                }
            ],
        },
        "--contract",
        "contract.json",
    )
    assert out_of_scope.returncode == 2
    assert not marker.exists()


def test_contract_binds_declared_scope_and_authority_to_receipt(tmp_path: Path) -> None:
    contract = json.loads(
        (ROOT / "plugins/1000x-engineer/skills/1000x-engineer/resources/task-contract.example.json").read_text()
    )
    (tmp_path / "contract.json").write_text(json.dumps(contract), encoding="utf-8")
    result = run_receipt(
        tmp_path,
        {
            "version": 2,
            "graders": [
                {
                    **grader("contract-pass", [sys.executable, "-c", "pass"]),
                    "access": contract_access(read_paths=["tests"]),
                }
            ],
        },
        "--contract",
        "contract.json",
    )
    assert result.returncode == 0, result.stderr
    receipt = json.loads((tmp_path / "RUN_RECEIPT.json").read_text())
    assert receipt["contract"]["scope"] == contract["scope"]
    assert receipt["contract"]["authority"] == contract["authority"]


def test_final_receipt_validates_against_its_draft_schema(tmp_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    result = run_receipt(
        tmp_path,
        {"version": 2, "graders": [grader("pass", [sys.executable, "-c", "pass"])]},
    )
    assert result.returncode == 0, result.stderr
    schema = json.loads(
        (ROOT / "plugins/1000x-engineer/skills/1000x-engineer/resources/receipt.schema.json").read_text()
    )
    receipt = json.loads((tmp_path / "RUN_RECEIPT.json").read_text())
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(receipt)


def test_grader_timeout_handled_properly(tmp_path: Path) -> None:
    manifest = {
        "version": 2,
        "graders": [
            {
                "id": "timeout-grader",
                "argv": [sys.executable, "-c", "import time; time.sleep(5)"],
                "timeout_seconds": 0.2,
                "required": True,
            }
        ],
    }
    result = run_receipt(tmp_path, manifest)
    assert result.returncode == 1
    receipt = json.loads((tmp_path / "RUN_RECEIPT.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "FAILED"
    assert receipt["graders"][0]["returncode"] == -124
    assert receipt["graders"][0]["status"] == "FAIL"


def test_grader_oserror_causes_aborted_status(tmp_path: Path) -> None:
    manifest = {
        "version": 2,
        "graders": [
            {
                "id": "nonexistent-cmd",
                "argv": ["nonexistent_executable_123456789"],
                "timeout_seconds": 10,
                "required": True,
            }
        ],
    }
    result = run_receipt(tmp_path, manifest)
    assert result.returncode == 2
    receipt = json.loads((tmp_path / "RUN_RECEIPT.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "ABORTED"
    assert receipt["graders"][0]["status"] == "ABORTED"


def test_subdirectory_output_validates_against_schema(tmp_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    out_subdir = "nested/artifacts"
    result = run_receipt(
        tmp_path,
        {"version": 2, "graders": [grader("pass", [sys.executable, "-c", "pass"])]},
        "--output-dir",
        out_subdir,
    )
    assert result.returncode == 0, result.stderr
    schema = json.loads(
        (ROOT / "plugins/1000x-engineer/skills/1000x-engineer/resources/receipt.schema.json").read_text()
    )
    receipt_file = tmp_path / out_subdir / "RUN_RECEIPT.json"
    assert receipt_file.is_file()
    receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(receipt)

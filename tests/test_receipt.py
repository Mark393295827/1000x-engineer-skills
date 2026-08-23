from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "plugins/1000x-engineer/skills/1000x-engineer/scripts/generate_run_receipt.py"


def run_receipt(tmp_path: Path, manifest: dict) -> subprocess.CompletedProcess[str]:
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(tmp_path), "--manifest", "manifest.json"],
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
            "graders": [{"id": "python", "argv": [sys.executable, "-c", "print('ok')"]}],
        },
    )
    assert result.returncode == 0, result.stderr
    receipt = json.loads((tmp_path / "RUN_RECEIPT.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "VERIFIED"
    assert receipt["graders"][0]["status"] == "PASS"
    assert receipt["artifacts"][0]["path"] == "artifact.txt"
    assert len(receipt["artifacts"][0]["sha256"]) == 64
    assert (tmp_path / "RUN_RECEIPT.md").is_file()
    assert (tmp_path / "RUN_RECEIPT.json.sha256").is_file()
    assert (tmp_path / ".evidence/logs/python.log").is_file()


def test_empty_required_graders_are_insufficient(tmp_path: Path) -> None:
    result = run_receipt(tmp_path, {"version": 2, "graders": []})
    assert result.returncode == 2
    assert json.loads((tmp_path / "RUN_RECEIPT.json").read_text())["status"] == "INSUFFICIENT_EVIDENCE"


def test_required_failure_is_failed(tmp_path: Path) -> None:
    result = run_receipt(
        tmp_path,
        {"version": 2, "graders": [{"id": "failure", "argv": [sys.executable, "-c", "raise SystemExit(3)"]}]},
    )
    assert result.returncode == 1
    assert json.loads((tmp_path / "RUN_RECEIPT.json").read_text())["status"] == "FAILED"


def test_manifest_rejects_path_like_grader_id(tmp_path: Path) -> None:
    result = run_receipt(
        tmp_path,
        {"version": 2, "graders": [{"id": "../escape", "argv": [sys.executable, "-c", "pass"]}]},
    )
    assert result.returncode == 2
    assert not (tmp_path.parent / "escape.log").exists()

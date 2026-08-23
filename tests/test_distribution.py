from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
PLUGIN_SKILL = ROOT / "plugins/1000x-engineer/skills/1000x-engineer"
SYNC = ROOT / "scripts/sync_compatibility_mirrors.py"
IGNORED_PARTS = {"__pycache__", ".DS_Store"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file() and not (set(path.parts) & IGNORED_PARTS) and path.suffix not in IGNORED_SUFFIXES
    }


def test_canonical_and_complete_compatibility_mirrors_are_synchronized() -> None:
    canonical = tree_hashes(PLUGIN_SKILL)
    for mirror in [ROOT / "skills/1000x-engineer", ROOT / ".agents/skills/1000x-engineer"]:
        assert tree_hashes(mirror) == canonical
    result = subprocess.run([sys.executable, str(SYNC), "--check"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_skill_validator_accepts_every_distributed_package() -> None:
    validator = PLUGIN_SKILL / "scripts/validate_skill.py"
    for skill in [PLUGIN_SKILL, ROOT / "skills/1000x-engineer", ROOT / ".agents/skills/1000x-engineer"]:
        result = subprocess.run([sys.executable, str(validator), str(skill)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr


def test_plugin_manifest_and_canonical_skill_exist() -> None:
    manifest_path = ROOT / "plugins/1000x-engineer/.codex-plugin/plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["name"] == "1000x-engineer"
    assert manifest["version"] == "1.0.0"
    assert manifest["skills"] == "./skills/"
    assert (PLUGIN_SKILL / "SKILL.md").is_file()


def test_sync_mirrors_detects_drift_and_reports_code_1() -> None:
    # Introduce deliberate temporary drift in one mirror to assert exit code 1
    mirror_status = ROOT / "skills/1000x-engineer/STATUS"
    original = mirror_status.read_bytes()
    try:
        mirror_status.write_bytes(b"DRIFT_STATUS_TEST\n")
        proc_drift = subprocess.run([sys.executable, str(SYNC), "--check"], capture_output=True, text=True)
        assert proc_drift.returncode == 1
        assert "mirror drift" in proc_drift.stderr
    finally:
        mirror_status.write_bytes(original)

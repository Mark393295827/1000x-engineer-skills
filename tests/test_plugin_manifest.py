from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_plugin_manifest_and_canonical_skill_exist() -> None:
    manifest_path = ROOT / "plugins/1000x-engineer/.codex-plugin/plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["name"] == "1000x-engineer"
    assert manifest["version"] == "1.0.0"
    assert manifest["skills"] == "./skills/"
    assert (ROOT / "plugins/1000x-engineer/skills/1000x-engineer/SKILL.md").is_file()


def test_validate_plugin_cli_success_and_failures(tmp_path: Path) -> None:
    import subprocess
    import sys

    validate_script = ROOT / "scripts/validate_plugin.py"

    # 1. Valid plugin directory
    proc = subprocess.run(
        [sys.executable, str(validate_script), str(ROOT / "plugins/1000x-engineer")],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "valid plugin" in proc.stdout

    # 2. Corrupted manifest (non-dict array)
    bad_plugin = tmp_path / "bad_plugin"
    bad_plugin_meta = bad_plugin / ".codex-plugin"
    bad_plugin_meta.mkdir(parents=True)
    (bad_plugin_meta / "plugin.json").write_text("[1, 2, 3]", encoding="utf-8")
    proc_bad = subprocess.run(
        [sys.executable, str(validate_script), str(bad_plugin)], capture_output=True, text=True
    )
    assert proc_bad.returncode == 1
    assert "invalid plugin manifest" in proc_bad.stderr

    # 3. Missing required skills directory
    (bad_plugin_meta / "plugin.json").write_text(
        json.dumps(
            {
                "name": "bad",
                "version": "1.0.0",
                "description": "desc",
                "skills": "./nonexistent_skills/",
            }
        ),
        encoding="utf-8",
    )
    proc_missing = subprocess.run(
        [sys.executable, str(validate_script), str(bad_plugin)], capture_output=True, text=True
    )
    assert proc_missing.returncode == 1
    assert "missing skills directory" in proc_missing.stderr

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
PLUGIN_SKILL = ROOT / "plugins/1000x-engineer/skills/1000x-engineer"


def test_canonical_and_compatibility_scripts_are_synchronized() -> None:
    for mirror in [ROOT / "skills/1000x-engineer", ROOT / ".agents/skills/1000x-engineer"]:
        for name in ["generate_run_receipt.py", "extract_skill_trace.py", "validate_skill.py"]:
            assert (PLUGIN_SKILL / "scripts" / name).read_bytes() == (mirror / "scripts" / name).read_bytes()


def test_skill_validator_and_manifest_shape() -> None:
    validator = PLUGIN_SKILL / "scripts/validate_skill.py"
    result = subprocess.run(
        [sys.executable, str(validator), str(PLUGIN_SKILL)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    manifest = json.loads((ROOT / "plugins/1000x-engineer/.codex-plugin/plugin.json").read_text())
    assert manifest["skills"].startswith("./")

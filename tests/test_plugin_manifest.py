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

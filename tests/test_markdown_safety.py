from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "plugins/1000x-engineer/skills/1000x-engineer/scripts/generate_run_receipt.py"


def test_markdown_escapes_delimiters_and_redacts_secrets(tmp_path: Path) -> None:
    manifest = {
        "version": 2,
        "graders": [
            {
                "id": "unsafe-grader",
                "argv": [sys.executable, "-c", "print('token=supersecret | `fence`')"],
                "timeout_seconds": 300,
                "required": True,
            }
        ],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(tmp_path), "--manifest", "manifest.json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    markdown = (tmp_path / "RUN_RECEIPT.md").read_text(encoding="utf-8")
    assert "supersecret" not in markdown
    assert "token=[REDACTED]" in markdown
    assert "\\|" in markdown and "\\`" in markdown

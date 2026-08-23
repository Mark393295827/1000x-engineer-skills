from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "plugins/1000x-engineer/skills/1000x-engineer/scripts/extract_skill_trace.py"


def test_skillify_creates_candidate_package(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--name",
            "fix-race",
            "--desc",
            "Use for a race",
            "--out-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    target = tmp_path / "fix-race"
    for relative in [
        "SKILL.md",
        "references/regression.md",
        "evals/positive-activation.md",
        "evals/negative-activation.md",
        "evals/activation-cases.json",
        "regression.yaml",
        "lifecycle.json",
        "references/lifecycle-policy.md",
        "STATUS",
    ]:
        assert (target / relative).is_file()
    assert (target / "STATUS").read_text().strip() == "CANDIDATE"
    validator = ROOT / "plugins/1000x-engineer/skills/1000x-engineer/scripts/validate_skill.py"
    validated = subprocess.run([sys.executable, str(validator), str(target)], capture_output=True, text=True)
    assert validated.returncode == 0, validated.stderr


def test_skillify_rejects_invalid_name_and_overwrite(tmp_path: Path) -> None:
    invalid = subprocess.run(
        [sys.executable, str(SCRIPT), "--name", "../escape", "--desc", "bad", "--out-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert invalid.returncode == 2
    first = subprocess.run(
        [sys.executable, str(SCRIPT), "--name", "existing", "--desc", "one", "--out-dir", str(tmp_path)],
        check=False,
    )
    second = subprocess.run(
        [sys.executable, str(SCRIPT), "--name", "existing", "--desc", "two", "--out-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert first.returncode == 0
    assert second.returncode == 2


def test_skillify_overwrite_flag_and_multiline_description(tmp_path: Path) -> None:
    multiline_desc = "First line of description.\nSecond line with more context."
    first = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--name",
            "overwrite-target",
            "--desc",
            multiline_desc,
            "--out-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert first.returncode == 0
    skill_content = (tmp_path / "overwrite-target/SKILL.md").read_text(encoding="utf-8")
    assert "First line of description." in skill_content
    assert "Second line with more context." in skill_content

    # Now overwrite with updated fields
    updated_desc = "New single line description."
    second = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--name",
            "overwrite-target",
            "--desc",
            updated_desc,
            "--out-dir",
            str(tmp_path),
            "--overwrite",
        ],
        capture_output=True,
        text=True,
    )
    assert second.returncode == 0
    updated_content = (tmp_path / "overwrite-target/SKILL.md").read_text(encoding="utf-8")
    assert "New single line description." in updated_content

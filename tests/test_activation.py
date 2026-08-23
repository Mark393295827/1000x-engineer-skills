from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "plugins/1000x-engineer/skills/1000x-engineer"


def test_activation_contract_is_specific_and_has_lifecycle() -> None:
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert "name: 1000x-engineer" in content
    assert "description:" in content
    assert "Evidence precedes mutation" in content
    assert "Run Receipts" in content or "receipt" in content.lower()
    assert (SKILL / "evals/positive-activation.md").is_file()
    assert (SKILL / "evals/negative-activation.md").is_file()

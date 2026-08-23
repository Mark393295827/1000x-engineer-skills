from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "plugins/1000x-engineer/skills/1000x-engineer"
VALIDATOR = SKILL / "scripts/validate_skill.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("lifecycle_validator", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_skill(tmp_path: Path) -> Path:
    target = tmp_path / "1000x-engineer"
    for source in SKILL.rglob("*"):
        destination = target / source.relative_to(SKILL)
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())
    return target


def test_reviewed_skill_requires_review_evidence_and_matching_status(tmp_path: Path) -> None:
    validator = load_validator()
    candidate = copy_skill(tmp_path)
    (candidate / "evidence/review.json").unlink()
    assert any("review.json" in error for error in validator.validate_skill(candidate))
    (candidate / "evidence").mkdir(exist_ok=True)
    (candidate / "evidence/review.json").write_text(
        json.dumps(json.loads((SKILL / "evidence/review.json").read_text())), encoding="utf-8"
    )
    (candidate / "STATUS").write_text("EVAL_PASS\n", encoding="utf-8")
    assert any("regression.yaml status" in error for error in validator.validate_skill(candidate))


def test_release_gate_rejects_reviewed_status() -> None:
    validator = load_validator()
    errors = validator.validate_skill(SKILL, minimum_status="EVAL_PASS", expected_version="1.0.0")
    assert any("below required EVAL_PASS" in error for error in errors)

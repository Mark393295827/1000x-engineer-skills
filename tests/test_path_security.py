from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]


def load(module_name: str, relative: str):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_receipt_containment_rejects_escape() -> None:
    module = load(
        "receipt_security", "plugins/1000x-engineer/skills/1000x-engineer/scripts/generate_run_receipt.py"
    )
    with pytest.raises(ValueError):
        module.ensure_contained(Path("C:/repo"), Path("C:/outside"))


def test_skillify_target_is_contained(tmp_path: Path) -> None:
    module = load(
        "skillify_security", "plugins/1000x-engineer/skills/1000x-engineer/scripts/extract_skill_trace.py"
    )
    assert module.safe_target(tmp_path, "safe-skill") == (tmp_path / "safe-skill").resolve()
    with pytest.raises(ValueError):
        module.safe_target(tmp_path, "../outside")


def test_validate_scope_path_rejects_drive_and_absolute_paths() -> None:
    module = load(
        "receipt_security", "plugins/1000x-engineer/skills/1000x-engineer/scripts/generate_run_receipt.py"
    )
    with pytest.raises(ValueError):
        module.validate_scope_path("C:/System/Path", "scope")
    with pytest.raises(ValueError):
        module.validate_scope_path("/absolute/path", "scope")
    with pytest.raises(ValueError):
        module.validate_scope_path("relative/../escape", "scope")
    assert module.validate_scope_path("src/valid", "scope") == "src/valid"

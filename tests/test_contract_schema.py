from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "plugins/1000x-engineer/skills/1000x-engineer/scripts/validate_contract.py"
EXAMPLE = ROOT / "plugins/1000x-engineer/skills/1000x-engineer/resources/task-contract.example.json"


def load_validator():
    spec = importlib.util.spec_from_file_location("contract_validator", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_example_enforces_authority_budget_and_scope() -> None:
    validator = load_validator()
    contract = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    validator.validate_contract(contract)


def test_contract_example_validates_against_draft_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        (ROOT / "plugins/1000x-engineer/skills/1000x-engineer/resources/task-contract.schema.json").read_text()
    )
    jsonschema.Draft202012Validator(schema).validate(json.loads(EXAMPLE.read_text()))


@pytest.mark.parametrize(
    "mutate",
    [
        lambda contract: contract["authority"].pop("deploy"),
        lambda contract: contract["budget"].update({"unbounded": True}),
        lambda contract: contract["scope"].update({"surprise": ["all"]}),
        lambda contract: contract.update({"undeclared": "value"}),
    ],
)
def test_contract_rejects_missing_or_undeclared_semantics(mutate) -> None:
    validator = load_validator()
    contract = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    mutate(contract)
    with pytest.raises(ValueError):
        validator.validate_contract(contract)


def test_validate_contract_cli_execution(tmp_path: Path) -> None:
    import subprocess
    import sys

    # 1. Success on valid contract
    proc = subprocess.run([sys.executable, str(SCRIPT), str(EXAMPLE)], capture_output=True, text=True)
    assert proc.returncode == 0
    assert "valid contract" in proc.stdout

    # 2. Rejection on invalid contract (e.g. path traversal)
    bad_contract = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    bad_contract["scope"]["included"] = ["../outside"]
    bad_file = tmp_path / "bad_contract.json"
    bad_file.write_text(json.dumps(bad_contract), encoding="utf-8")

    proc_bad = subprocess.run([sys.executable, str(SCRIPT), str(bad_file)], capture_output=True, text=True)
    assert proc_bad.returncode == 1
    assert "invalid contract" in proc_bad.stderr


def test_contract_rejects_drive_letter_path() -> None:
    validator = load_validator()
    contract = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    contract["scope"]["included"] = ["C:/Windows/System32"]
    with pytest.raises(ValueError):
        validator.validate_contract(contract)

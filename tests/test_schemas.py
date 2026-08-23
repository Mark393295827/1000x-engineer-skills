from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
RESOURCES = ROOT / "plugins/1000x-engineer/skills/1000x-engineer/resources"


def test_all_json_schemas_are_valid_draft_2020_12() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    for path in [
        RESOURCES / "grader-manifest.schema.json",
        RESOURCES / "receipt.schema.json",
        RESOURCES / "task-contract.schema.json",
    ]:
        jsonschema.Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))

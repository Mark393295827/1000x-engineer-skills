from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "plugins/1000x-engineer/skills/1000x-engineer"
EVALUATOR = SKILL / "scripts/evaluate_activation.py"


def load_evaluator():
    spec = importlib.util.spec_from_file_location("activation_evaluator", EVALUATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_activation_suite_has_behavioral_positive_negative_and_ambiguous_cases() -> None:
    evaluator = load_evaluator()
    payload = json.loads((SKILL / "evals/activation-cases.json").read_text(encoding="utf-8"))
    cases = evaluator.validate_cases(payload)
    assert len(cases) == 50
    destructive = next(case for case in cases if case["id"] == "positive-20")
    assert destructive["expected"] == {"activate": True, "first_action": "pause_for_authority"}


def test_activation_evaluator_scores_recorded_responses() -> None:
    evaluator = load_evaluator()
    cases = evaluator.validate_cases(
        json.loads((SKILL / "evals/activation-cases.json").read_text(encoding="utf-8"))
    )
    responses = [
        {
            "id": case["id"],
            "activate": case["expected"]["activate"],
            "first_action": case["expected"]["first_action"],
        }
        for case in cases
    ]
    result = evaluator.score(cases, responses)
    assert result["status"] == "EVAL_PASS"
    assert result["accuracy"] == 1.0
    responses[0]["activate"] = False
    assert evaluator.score(cases, responses)["status"] == "FAILED"


def test_evaluate_activation_cli_pass_fail_and_error(tmp_path: Path) -> None:
    cases_path = SKILL / "evals/activation-cases.json"
    cases_data = json.loads(cases_path.read_text(encoding="utf-8"))
    responses = {
        "responses": [
            {
                "id": c["id"],
                "activate": c["expected"]["activate"],
                "first_action": c["expected"]["first_action"],
            }
            for c in cases_data["cases"]
        ]
    }
    resp_file = tmp_path / "responses.json"
    out_file = tmp_path / "eval_out.json"
    resp_file.write_text(json.dumps(responses), encoding="utf-8")

    import subprocess
    import sys

    # 1. Successful run -> returncode 0 and writes output
    proc = subprocess.run(
        [
            sys.executable,
            str(EVALUATOR),
            "--cases",
            str(cases_path),
            "--responses",
            str(resp_file),
            "--output",
            str(out_file),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert out_file.is_file()
    assert json.loads(out_file.read_text(encoding="utf-8"))["status"] == "EVAL_PASS"

    # 2. Failed accuracy -> returncode 1
    responses["responses"][0]["activate"] = not responses["responses"][0]["activate"]
    resp_file.write_text(json.dumps(responses), encoding="utf-8")
    proc_fail = subprocess.run(
        [sys.executable, str(EVALUATOR), "--cases", str(cases_path), "--responses", str(resp_file)],
        capture_output=True,
        text=True,
    )
    assert proc_fail.returncode == 1
    assert "FAILED" in proc_fail.stdout

    # 3. Invalid JSON payload -> returncode 2
    resp_file.write_text("invalid json payload", encoding="utf-8")
    proc_err = subprocess.run(
        [sys.executable, str(EVALUATOR), "--cases", str(cases_path), "--responses", str(resp_file)],
        capture_output=True,
        text=True,
    )
    assert proc_err.returncode == 2

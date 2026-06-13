"""Tests for the evaluation runner script.

Verifies test case loading and report formatting using PydanticAI's TestModel.
"""

import json
from pathlib import Path
from pydantic_ai.models.test import TestModel
from agent import agent
from evaluation.run_evals import load_test_cases, run_evaluation, judge_agent


def test_load_test_cases(tmp_path: Path) -> None:
    """Test that test cases are loaded correctly from JSON file."""
    data = {
        "test_cases": [
            {
                "test_case_id": 1,
                "question": "Test question?",
                "type": "Test Type",
                "expected_key_facts": [],
                "expected_sources": [],
                "expected_facts_omitted": [],
            }
        ]
    }
    file_path = tmp_path / "test_eval.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    test_cases = load_test_cases(file_path)
    assert len(test_cases) == 1
    assert test_cases[0]["question"] == "Test question?"
    assert test_cases[0]["type"] == "Test Type"


def test_run_evaluation() -> None:
    """Test that run_evaluation generates a valid Markdown report with agent overrides."""
    test_cases = [
        {
            "test_case_id": 1,
            "question": "What is the discount window?",
            "type": "Single-source factual",
            "expected_key_facts": ["fact1"],
            "expected_sources": ["source1"],
            "expected_facts_omitted": ["omit1"],
        }
    ]

    model = TestModel(custom_output_text="Mocked evaluation response")
    judge_model = TestModel(custom_output_args={"pass_fail": "Pass", "reasoning": "Mocked judge reasoning"})

    with agent.override(model=model), judge_agent.override(model=judge_model):
        report = run_evaluation(test_cases)

    assert "# Titan Research Agent Evaluation Results" in report
    assert "Overall Success Metrics" in report
    assert "Overall Success Rate" in report
    assert "| 1 | Single-source factual | What is the discount window? | Success | **Pass** |" in report
    assert "### Test Case 1: What is the discount window?" in report
    assert "**Judge Status**: **Pass**" in report
    assert "Mocked judge reasoning" in report
    assert "Mocked evaluation response" in report

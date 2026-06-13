"""Script to run evaluation questions and compile the results in Markdown format.

This module executes the evaluation test cases using the research agent,
runs an LLM-as-a-judge to grade the responses based on expected key facts,
expected sources, and expected facts omitted, and formats the output into
a comprehensive Markdown report.
"""

import datetime
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Literal

# Add the parent directory to sys.path so we can import the agent
sys.path.append(str(Path(__file__).parent.parent))

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from agent import agent  # noqa: E402


class EvaluationResult(BaseModel):
    """Pydantic model representing the output schema for the LLM judge evaluation.

    Attributes:
        pass_fail: Whether the agent's response passed or failed evaluation criteria.
        reasoning: Detailed reasoning for the pass/fail score.
    """

    pass_fail: Literal["Pass", "Fail"] = Field(
        ...,
        description="Either 'Pass' or 'Fail' indicating whether the agent response met the criteria."
    )
    reasoning: str = Field(
        ...,
        description="Detailed explanation of the pass/fail score, detailing which expected facts, sources, or omitted facts were satisfied or not."
    )


# Instantiate the LLM-as-a-judge agent using the same model as the main agent
judge_agent = Agent(
    "groq:meta-llama/llama-4-scout-17b-16e-instruct", # TODO: use a better model for this
    output_type=EvaluationResult,
    system_prompt=(
        "You are an objective LLM judge evaluating the performance of a research agent.\n"
        "You will be given:\n"
        "1. The original question.\n"
        "2. The agent's generated response.\n"
        "3. A list of expected key facts that the response should contain.\n"
        "4. A list of expected sources/tools that should have been cited or used.\n"
        "5. A list of facts/topics that should NOT have been mentioned (facts omitted).\n\n"
        "Criteria for a 'Pass':\n"
        "- The response must address the question directly.\n"
        "- The response must cover a majority of the expected key facts accurately.\n"
        "- The response must cite/reference the expected sources (e.g., arXiv, FRED, Wikipedia) if applicable.\n"
        "- The response must NOT contain information that should be omitted.\n\n"
        "Provide a detailed reasoning explaining your decision, then output 'Pass' or 'Fail' for the pass_fail field."
    ),
)


def load_test_cases(file_path: Path) -> List[Dict[str, Any]]:
    """Loads evaluation test cases from the specified JSON file.

    Args:
        file_path: Path to the JSON file containing test cases.

    Returns:
        A list of dictionaries representing the test cases.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Evaluation file not found at: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("test_cases", [])


def run_evaluation(test_cases: List[Dict[str, Any]]) -> str:
    """Runs all test cases through the agent and generates a Markdown report.

    Args:
        test_cases: List of test case dictionaries.

    Returns:
        The content of the Markdown report as a string.
    """
    results: List[Dict[str, Any]] = []
    passes = 0
    fails = 0

    for tc in test_cases:
        tc_id = tc.get("test_case_id", "Unknown")
        question = tc.get("question", "")
        tc_type = tc.get("type", "Unknown")
        expected_key_facts = tc.get("expected_key_facts", [])
        expected_sources = tc.get("expected_sources", [])
        expected_facts_omitted = tc.get("expected_facts_omitted", [])

        print(f"Running Test Case {tc_id}/{len(test_cases)}: {question[:50]}...")

        status = "Success"
        response_text = ""
        try:
            result = agent.run_sync(question)
            response_text = str(result.output)
        except Exception as e:
            status = f"Error: {e}"
            response_text = f"An error occurred: {e}"
            print(f"  Error on Test Case {tc_id}: {e}")

        # If execution succeeded, evaluate with LLM-as-a-judge
        judge_status = "Fail"
        judge_reasoning = ""

        if status == "Success":
            judge_prompt = (
                f"Question: {question}\n\n"
                f"Agent Response:\n{response_text}\n\n"
                f"Expected Key Facts:\n{expected_key_facts}\n\n"
                f"Expected Sources/Tools:\n{expected_sources}\n\n"
                f"Expected Facts Omitted:\n{expected_facts_omitted}\n"
            )
            print(f"  Running LLM-as-a-judge for Test Case {tc_id}...")
            try:
                judge_res = judge_agent.run_sync(judge_prompt)
                judge_status = judge_res.output.pass_fail
                judge_reasoning = judge_res.output.reasoning
            except Exception as je:
                judge_status = "Fail"
                judge_reasoning = f"LLM judge failed to evaluate: {je}"
                print(f"  Judge Error on Test Case {tc_id}: {je}")
        else:
            judge_reasoning = f"Skipped evaluation because agent run failed with error: {status}"

        if judge_status == "Pass":
            passes += 1
        else:
            fails += 1

        results.append(
            {
                "id": tc_id,
                "question": question,
                "type": tc_type,
                "status": status,
                "response": response_text,
                "judge_status": judge_status,
                "judge_reasoning": judge_reasoning,
            }
        )

    # Compute overall statistics
    total = len(test_cases)
    success_rate = (passes / total * 100) if total > 0 else 0.0

    report_lines: List[str] = []
    report_lines.append("# Titan Research Agent Evaluation Results\n")
    report_lines.append(f"**Run Date**: {datetime.datetime.now().isoformat()}\n")
    report_lines.append(f"**Model**: `{agent.model.model_name}`\n")
    report_lines.append("## Overall Success Metrics\n")
    report_lines.append(f"- **Total Test Cases**: {total}")
    report_lines.append(f"- **Passed**: {passes}")
    report_lines.append(f"- **Failed**: {fails}")
    report_lines.append(f"- **Overall Success Rate**: {success_rate:.1f}%\n")

    # Generate Summary Table
    report_lines.append("## Evaluation Summary\n")
    report_lines.append("| ID | Type | Question | Execution Status | Judge Status |")
    report_lines.append("|---|---|---|---|---|")

    for r in results:
        question_escaped = r["question"].replace("|", "\\|")
        report_lines.append(
            f"| {r['id']} | {r['type']} | {question_escaped} | {r['status']} | **{r['judge_status']}** |"
        )

    report_lines.append("\n---\n")

    # Generate Detailed Section
    report_lines.append("## Detailed Responses\n")
    for r in results:
        report_lines.append(f"### Test Case {r['id']}: {r['question']}")
        report_lines.append(f"**Type**: {r['type']}\n")
        report_lines.append(f"**Execution Status**: {r['status']}\n")
        report_lines.append(f"**Judge Status**: **{r['judge_status']}**\n")
        report_lines.append(f"**Judge Reasoning**:\n{r['judge_reasoning']}\n")
        report_lines.append("#### Agent Response")
        report_lines.append(r["response"])
        report_lines.append("\n---\n")

    return "\n".join(report_lines)


def main() -> None:
    """Main execution function to load test cases, run evaluation, and save results."""
    # Ensure GROQ_API_KEY is available
    if not os.environ.get("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    eval_dir = Path(__file__).parent
    eval_data_path = eval_dir / "eval_data.json"
    results_path = eval_dir / "eval_results.md"

    try:
        test_cases = load_test_cases(eval_data_path)
        report = run_evaluation(test_cases)

        with open(results_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\nEvaluation complete. Results saved to: {results_path}")

    except Exception as e:
        print(f"Error running evaluation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

"""Script to run evaluation questions and compile the results in Markdown format."""

import datetime
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add the parent directory to sys.path so we can import the agent
sys.path.append(str(Path(__file__).parent.parent))

from agent import agent  # noqa: E402


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
    report_lines: List[str] = []
    report_lines.append("# Titan Research Agent Evaluation Results\n")
    report_lines.append(f"**Run Date**: {datetime.datetime.now().isoformat()}\n")
    report_lines.append(f"**Model**: `{agent.model.model_name}`\n")

    # Generate Summary Table
    report_lines.append("## Evaluation Summary\n")
    report_lines.append("| ID | Type | Question | Status |")
    report_lines.append("|---|---|---|---|")

    results: List[Dict[str, Any]] = []

    for tc in test_cases:
        tc_id = tc.get("test_case_id", "Unknown")
        question = tc.get("question", "")
        tc_type = tc.get("type", "Unknown")

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

        # Add to summary table
        question_escaped = question.replace("|", "\\|")
        report_lines.append(f"| {tc_id} | {tc_type} | {question_escaped} | {status} |")

        results.append(
            {
                "id": tc_id,
                "question": question,
                "type": tc_type,
                "status": status,
                "response": response_text,
            }
        )

    report_lines.append("\n---\n")

    # Generate Detailed Section
    report_lines.append("## Detailed Responses\n")
    for r in results:
        report_lines.append(f"### Test Case {r['id']}: {r['question']}")
        report_lines.append(f"**Type**: {r['type']}\n")
        report_lines.append(f"**Execution Status**: {r['status']}\n")
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

"""Titan Research Agent.

An AI-powered agent designed for financial and regulatory research using PydanticAI
and Groq. It supports searching academic papers via arXiv and macroeconomic series
via FRED, synthesizing a final response with structured citations.
"""

import datetime
import json
import os
import sys
from dataclasses import is_dataclass
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent, ModelSettings
from pydantic_ai.run import AgentRunResult
from tools import ArXivSearchTool, FredSearchTool

# Load environment variables from .env
load_dotenv()

# Instantiate dummy tools
arxiv_tool = ArXivSearchTool()
fred_tool = FredSearchTool()

# Define the research agent
agent = Agent(
    # "groq:llama-3.1-8b-instant",
    "groq:meta-llama/llama-4-scout-17b-16e-instruct",
    model_settings=ModelSettings(temperature=0.0),
    system_prompt=(
        "You are an expert financial and regulatory research assistant.\n"
        "Your task is to answer user questions using information from the arXiv (academic papers) and FRED (Federal Reserve Economic Data) search tools.\n\n"
        "Use the search tools to retrieve accurate facts. Synthesize the findings into a clear response, providing inline citations and a structured sources list at the end."
    ),
)


@agent.tool_plain
def search_arxiv(query: str) -> str:
    """Search academic papers on arXiv.

    Supports simple search terms or structured queries using field prefixes:
    - ti: Title (e.g. ti:"credit risk")
    - abs: Abstract (e.g. abs:"machine learning")
    - cat: Subject Category (e.g. cat:q-fin.RM for Risk Management)
    - au: Author (e.g. au:delbaen)
    - all: All fields (default if no prefix is provided)

    Combine queries with capitalized boolean operators (AND, OR, ANDNOT).
    Example: ti:"credit risk" AND cat:q-fin.RM

    Args:
        query: The search term or structured query.

    Returns:
        A formatted string detailing matching papers and their contents.
    """
    res = arxiv_tool.search(query)
    header = f"API Query URL: {res.api_query}\n\n" if res.api_query else ""
    if not res.items:
        return f"{header}No academic papers found on arXiv for: {query}"

    output = []
    for item in res.items:
        output.append(
            f"Title: {item.title}\n"
            f"ID: {item.id}\n"
            f"URL: {item.url}\n"
            f"Content: {item.content}\n"
            f"---"
        )
    return header + "\n".join(output)


@agent.tool_plain
def search_fred(query: str) -> str:
    """Search the Federal Reserve Economic Data (FRED) database.

    Economic data series — GDP, interest rates, unemployment.
    Use this tool for historical macroeconomic series, interest rates, the
    Federal Reserve's discount window rates, banking sector assets/equity data,
    and official financial indicators.

    Args:
        query: The search term or query.

    Returns:
        A formatted string detailing matching FRED data series.
    """
    res = fred_tool.search(query)
    header = f"API Query URL: {res.api_query}\n\n" if res.api_query else ""
    if not res.items:
        return f"{header}No data series found on FRED for: {query}"

    output = []
    for item in res.items:
        output.append(
            f"Title: {item.title}\n"
            f"ID: {item.id}\n"
            f"URL: {item.url}\n"
            f"Content: {item.content}\n"
            f"---"
        )
    return header + "\n".join(output)


def serialize_custom(obj: Any) -> Any:
    """Recursively serialize objects including datetime, Pydantic models, and dataclasses.

    Args:
        obj: The object to serialize.

    Returns:
        A JSON-serializable representation of the object.
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")
    if is_dataclass(obj):
        return {
            k: serialize_custom(v)
            for k, v in obj.__dict__.items()
            if not k.startswith("_")
        }
    if isinstance(obj, dict):
        return {k: serialize_custom(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [serialize_custom(v) for v in obj]
    return obj


def build_trace_data(question: str, result: AgentRunResult) -> Dict[str, Any]:
    """Build a structured trace dictionary from the agent run result.

    Args:
        question: The user's query question.
        result: The PydanticAI agent run result object.

    Returns:
        A dictionary containing steps, final synthesis, and raw conversation messages.
    """
    steps: List[Dict[str, Any]] = []
    tool_calls: Dict[str, Dict[str, Any]] = {}
    current_reasoning = ""
    messages = result.all_messages()

    for msg in messages:
        parts = getattr(msg, "parts", [])
        for part in parts:
            part_kind = getattr(part, "part_kind", "")
            if part_kind == "text":
                current_reasoning = getattr(part, "content", "")
            elif part_kind == "tool-call":
                tool_call_id = getattr(part, "tool_call_id", "")
                tool_name = getattr(part, "tool_name", "")
                args = getattr(part, "args", None)

                parsed_args = args
                if isinstance(args, str):
                    try:
                        parsed_args = json.loads(args)
                    except Exception:
                        pass

                tool_calls[tool_call_id] = {
                    "tool_selected": tool_name,
                    "tool_input": parsed_args,
                    "agent_reasoning": current_reasoning,
                }
            elif part_kind == "tool-return":
                tool_call_id = getattr(part, "tool_call_id", "")
                tool_name = getattr(part, "tool_name", "")
                content = getattr(part, "content", "")

                # Extract request_url if present in content
                request_url = None
                if content.startswith("API Query URL: "):
                    first_line = content.split("\n", 1)[0]
                    request_url = first_line.replace("API Query URL: ", "").strip()

                call_info = tool_calls.get(tool_call_id, {})
                steps.append({
                    "step_number": len(steps) + 1,
                    "tool_selected": call_info.get("tool_selected", tool_name),
                    "tool_input": call_info.get("tool_input"),
                    "request_url": request_url,
                    "raw_tool_output": content,
                    "agent_reasoning": call_info.get("agent_reasoning", ""),
                })

    serialized_messages = [serialize_custom(msg) for msg in messages]

    return {
        "question": question,
        "steps": steps,
        "final_synthesis": result.output,
        "messages": serialized_messages,
    }


def run_agent(question: str) -> str:
    """Execute the research agent on a given question.

    Args:
        question: The natural language research question.

    Returns:
        The synthesized answer returned by the agent.
    """
    result = agent.run_sync(question)
    return str(result.output)


def main() -> None:
    """Command-line entrypoint for the research agent."""
    if len(sys.argv) < 2:
        print("Usage: python agent.py \"<research question>\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    # Check for GROQ_API_KEY
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print(
            "Error: GROQ_API_KEY is not set in environment or .env file.\n"
            "Please create a .env file with your API key, for example:\n"
            "GROQ_API_KEY=your_groq_api_key_here",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        result = agent.run_sync(question)
        print(result.output)

        # Log trace to structured JSON file
        trace_data = build_trace_data(question, result)
        with open("run_trace.json", "w", encoding="utf-8") as f:
            json.dump(trace_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error executing research agent: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

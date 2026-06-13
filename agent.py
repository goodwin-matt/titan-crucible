"""Titan Research Agent.

An AI-powered agent designed for financial and regulatory research using PydanticAI
and Groq. It supports searching academic papers via arXiv and macroeconomic series
via FRED, synthesizing a final response with structured citations.
"""

import os
import sys
from typing import Optional
from dotenv import load_dotenv
from pydantic_ai import Agent, ModelSettings
from tools import ArXivSearchTool, FredSearchTool

# Load environment variables from .env
load_dotenv()

# Instantiate dummy tools
arxiv_tool = ArXivSearchTool()
fred_tool = FredSearchTool()

# Define the research agent
agent = Agent(
    "groq:llama-3.1-8b-instant",
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

    Use this tool for academic research, theoretical models, credit risk papers,
    and detailed regulatory standards like Basel III.

    Args:
        query: The search term or query.

    Returns:
        A formatted string detailing matching papers and their contents.
    """
    res = arxiv_tool.search(query)
    if not res.items:
        return f"No academic papers found on arXiv for: {query}"

    output = []
    for item in res.items:
        output.append(
            f"Title: {item.title}\n"
            f"ID: {item.id}\n"
            f"URL: {item.url}\n"
            f"Content: {item.content}\n"
            f"---"
        )
    return "\n".join(output)


@agent.tool_plain
def search_fred(query: str) -> str:
    """Search the Federal Reserve Economic Data (FRED) database.

    Use this tool for historical macroeconomic series, interest rates, the
    Federal Reserve's discount window rates, banking sector assets/equity data,
    and official financial indicators.

    Args:
        query: The search term or query.

    Returns:
        A formatted string detailing matching FRED data series.
    """
    res = fred_tool.search(query)
    if not res.items:
        return f"No data series found on FRED for: {query}"

    output = []
    for item in res.items:
        output.append(
            f"Title: {item.title}\n"
            f"ID: {item.id}\n"
            f"URL: {item.url}\n"
            f"Content: {item.content}\n"
            f"---"
        )
    return "\n".join(output)


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
        print("=== FINAL OUTPUT ===")
        print(result.output)
        print("\n=== CONVERSATION HISTORY ===")
        for msg in result.all_messages():
            print(msg)
    except Exception as e:
        print(f"Error executing research agent: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

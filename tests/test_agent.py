"""Tests for the research agent.

This module contains unit tests for the agent orchestration, verifying tool calling
and response generation using PydanticAI's TestModel.
"""

from pydantic_ai.models.test import TestModel
from agent import agent, run_agent


def test_agent_tool_calling_arxiv() -> None:
    """Test that the agent can be executed with a TestModel mock."""
    # Configure the test model
    model = TestModel(custom_output_text="Mocked response from TestModel")

    # Run the agent with overridden model
    with agent.override(model=model):
        response = run_agent("What is Basel III?")
        assert response == "Mocked response from TestModel"


from unittest.mock import MagicMock, patch
from agent import search_arxiv
from tests.test_tools import MOCK_ARXIV_XML

@patch("httpx.get")
def test_search_arxiv_tool_returns_query(mock_get: MagicMock) -> None:
    """Test that the search_arxiv tool wrapper returns the API query URL in the header."""
    mock_response = MagicMock()
    mock_response.content = MOCK_ARXIV_XML
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    output = search_arxiv("Basel III")
    assert "API Query URL: https://export.arxiv.org/api/query?search_query=all%3ABasel%20III&max_results=3" in output
    assert "Title: Basel III: A Global Regulatory Framework" in output


def test_build_trace_data() -> None:
    """Test that build_trace_data correctly parses PydanticAI messages into structured steps."""
    from agent import build_trace_data
    from pydantic_ai.messages import (
        ModelRequest,
        ModelResponse,
        TextPart,
        ToolCallPart,
        ToolReturnPart,
        SystemPromptPart,
        UserPromptPart,
    )

    # Mock result
    result = MagicMock()
    result.output = "Final synthesis text"

    # Create mock messages
    msg1 = ModelRequest(
        parts=[
            SystemPromptPart(content="system prompt context"),
            UserPromptPart(content="User query"),
        ]
    )
    # PydanticAI messages use kind="request" or "response"
    msg1.kind = "request"

    msg2 = ModelResponse(
        parts=[
            TextPart(content="Agent reasoning before tool call"),
            ToolCallPart(
                tool_name="search_arxiv",
                args={"query": "Basel III"},
                tool_call_id="call-123",
            ),
        ]
    )
    msg2.kind = "response"

    msg3 = ModelRequest(
        parts=[
            ToolReturnPart(
                tool_name="search_arxiv",
                content="API Query URL: https://export.arxiv.org/api/query?search_query=all%3ABasel%20III&max_results=3\n\nRaw search results",
                tool_call_id="call-123",
            )
        ]
    )
    msg3.kind = "request"

    result.all_messages.return_value = [msg1, msg2, msg3]

    trace = build_trace_data("What is Basel III?", result)

    assert trace["question"] == "What is Basel III?"
    assert trace["final_synthesis"] == "Final synthesis text"
    assert len(trace["steps"]) == 1

    step = trace["steps"][0]
    assert step["step_number"] == 1
    assert step["tool_selected"] == "search_arxiv"
    assert step["tool_input"] == {"query": "Basel III"}
    assert step["request_url"] == "https://export.arxiv.org/api/query?search_query=all%3ABasel%20III&max_results=3"
    assert "Raw search results" in step["raw_tool_output"]
    assert step["agent_reasoning"] == "Agent reasoning before tool call"
    assert len(trace["messages"]) == 3


from agent import search_wikipedia
from tests.test_tools import mock_wiki_get

@patch("httpx.get", side_effect=mock_wiki_get)
def test_search_wikipedia_tool_wrapper(mock_get: MagicMock) -> None:
    """Test that the search_wikipedia tool wrapper returns structured text including query URL."""
    output = search_wikipedia("Basel III")
    assert "API Query URL: https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=Basel%20III&format=json&srlimit=3" in output
    assert "Title: Basel III" in output
    assert "Content: Basel III is a global regulatory framework for banks..." in output




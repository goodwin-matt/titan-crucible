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

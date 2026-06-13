"""Base interface for research tools.

This module defines the common data models and abstract base class that all
research tools must implement to ensure a consistent interface.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field


class ToolResultItem(BaseModel):
    """A single result item from a search tool."""

    title: str = Field(
        ..., description="Title or name of the source document/series"
    )
    content: str = Field(
        ...,
        description="Relevant snippet, excerpt, or description of the content",
    )
    url: str = Field(..., description="Link to the original source")
    id: str = Field(
        ...,
        description="Unique identifier of the source (e.g., arXiv ID or FRED series ID)",
    )


class ToolResult(BaseModel):
    """The collection of results returned by a search tool."""

    source_name: str = Field(
        ..., description="The name of the source (e.g., arXiv, FRED)"
    )
    items: List[ToolResultItem] = Field(
        default_factory=list, description="List of search result items"
    )
    api_query: Optional[str] = Field(
        None, description="The actual API query or URL used for the search"
    )


class BaseResearchTool(ABC):
    """Abstract base class representing a research tool."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """The description of the tool to help the agent decide when to use it."""
        pass

    @abstractmethod
    def search(self, query: str) -> ToolResult:
        """Search the tool's database for the given query.

        Args:
            query: The search term or question.

        Returns:
            A ToolResult containing relevant documents or data.
        """
        pass

"""Wikipedia search tool calling the Wikipedia API.

This module provides a real implementation of the Wikipedia search tool.
"""

import re
import urllib.parse
import httpx
from tools.base import BaseResearchTool, ToolResult, ToolResultItem


class WikipediaSearchTool(BaseResearchTool):
    """A search tool that queries Wikipedia for summaries of articles."""

    @property
    def name(self) -> str:
        """The name of the tool."""
        return "wikipedia_search"

    @property
    def description(self) -> str:
        """The description of the tool to help the agent decide when to use it."""
        return (
            "Search Wikipedia. Use this tool for general knowledge, histories, quick summaries, "
            "biographies, overview of concepts, and background context."
        )

    def search(self, query: str) -> ToolResult:
        """Query Wikipedia search and summary APIs.

        Args:
            query: The search term or article title.

        Returns:
            A ToolResult containing the matching Wikipedia pages.
        """
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_query}&format=json&srlimit=3"
        headers = {
            "User-Agent": "TitanResearchAgent/1.0 (contact@example.com)"
        }

        try:
            response = httpx.get(search_url, headers=headers, timeout=10.0)
            response.raise_for_status()
            search_data = response.json()
            search_results = search_data.get("query", {}).get("search", [])

            items = []
            for item in search_results:
                title = item.get("title", "")
                if not title:
                    continue

                encoded_title = urllib.parse.quote(title)
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"

                try:
                    sum_resp = httpx.get(summary_url, headers=headers, timeout=5.0)
                    if sum_resp.status_code == 200:
                        sum_data = sum_resp.json()
                        extract = sum_data.get("extract", "No extract available.")
                        page_url = sum_data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{title}")

                        items.append(
                            ToolResultItem(
                                title=title,
                                content=extract,
                                url=page_url,
                                id=f"Wikipedia:{title}",
                            )
                        )
                except Exception:
                    # Fallback to search snippet if summary API fails
                    snippet = item.get("snippet", "No snippet available.")
                    clean_snippet = re.sub(r"<[^>]*>", "", snippet)
                    items.append(
                        ToolResultItem(
                            title=title,
                            content=clean_snippet,
                            url=f"https://en.wikipedia.org/wiki/{title}",
                            id=f"Wikipedia:{title}",
                        )
                    )

            return ToolResult(source_name="Wikipedia", items=items, api_query=search_url)

        except Exception as e:
            return ToolResult(
                source_name="Wikipedia",
                items=[
                    ToolResultItem(
                        title="Error calling Wikipedia API",
                        content=f"An error occurred while calling the Wikipedia API: {str(e)}",
                        url="https://en.wikipedia.org",
                        id="error",
                    )
                ],
                api_query=search_url,
            )

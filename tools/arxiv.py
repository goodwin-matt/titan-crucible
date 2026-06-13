"""arXiv search tool calling the live arXiv API.

This module provides a real implementation of the arXiv search tool.
"""

import urllib.parse
import xml.etree.ElementTree as ET
import httpx
from tools.base import BaseResearchTool, ToolResult, ToolResultItem


class ArXivSearchTool(BaseResearchTool):
    """A search tool that queries the live arXiv API for academic papers."""

    @property
    def name(self) -> str:
        """The name of the tool."""
        return "arxiv_search"

    @property
    def description(self) -> str:
        """The description of the tool to help the agent decide when to use it."""
        return (
            "Search academic papers on arXiv. Supports simple keywords and structured queries "
            "using prefixes (ti: Title, abs: Abstract, cat: Category, au: Author) and boolean "
            "operators (AND, OR, ANDNOT). Example: ti:\"credit risk\" AND cat:q-fin.RM"
        )

    def search(self, query: str) -> ToolResult:
        """Query the live arXiv API for papers.

        Args:
            query: The search term or structured query.

        Returns:
            A ToolResult containing the matching papers.
        """
        # Prepend 'all:' by default if no valid arXiv field prefixes are specified
        prefixes = ["all:", "ti:", "au:", "abs:", "co:", "jr:", "cat:", "rn:", "id:"]
        if not any(p in query for p in prefixes):
            full_query = f"all:{query}"
        else:
            full_query = query

        encoded_query = urllib.parse.quote(full_query)
        url = f"https://export.arxiv.org/api/query?search_query={encoded_query}&max_results=3"

        try:
            response = httpx.get(url, follow_redirects=True, timeout=10.0)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            items = []
            for entry in root.findall("atom:entry", ns):
                title_elem = entry.find("atom:title", ns)
                summary_elem = entry.find("atom:summary", ns)
                id_elem = entry.find("atom:id", ns)

                title = (
                    title_elem.text.strip().replace("\n", " ")
                    if title_elem is not None and title_elem.text
                    else "Unknown Title"
                )
                summary = (
                    summary_elem.text.strip().replace("\n", " ")
                    if summary_elem is not None and summary_elem.text
                    else "No summary available."
                )
                raw_id_url = (
                    id_elem.text.strip()
                    if id_elem is not None and id_elem.text
                    else ""
                )

                # Extract clean arXiv ID from URL, e.g. "http://arxiv.org/abs/1012.5678v1" -> "arXiv:1012.5678"
                arxiv_id = raw_id_url
                if "/abs/" in raw_id_url:
                    parts = raw_id_url.split("/abs/")
                    if len(parts) > 1:
                        # Strip version if present (e.g. v1)
                        clean_id = parts[1].split("v")[0]
                        arxiv_id = f"arXiv:{clean_id}"

                items.append(
                    ToolResultItem(
                        title=title,
                        content=summary,
                        url=raw_id_url or f"https://arxiv.org/abs/{arxiv_id}",
                        id=arxiv_id,
                    )
                )

            return ToolResult(source_name="arXiv", items=items, api_query=url)

        except Exception as e:
            return ToolResult(
                source_name="arXiv",
                items=[
                    ToolResultItem(
                        title="Error calling arXiv API",
                        content=f"An error occurred while calling the arXiv API: {str(e)}",
                        url="https://arxiv.org",
                        id="error",
                    )
                ],
                api_query=url,
            )

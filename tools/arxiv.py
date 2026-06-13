"""Dummy arXiv search tool.

This module provides a mock implementation of the arXiv search tool.
"""

from tools.base import BaseResearchTool, ToolResult, ToolResultItem


class ArXivSearchTool(BaseResearchTool):
    """A mock implementation of the arXiv search tool."""

    @property
    def name(self) -> str:
        """The name of the tool."""
        return "arxiv_search"

    @property
    def description(self) -> str:
        """The description of the tool to help the agent decide when to use it."""
        return (
            "Search academic papers on arXiv. Use this tool for academic research, "
            "theoretical models, credit risk papers, and detailed regulatory standards like Basel III."
        )

    def search(self, query: str) -> ToolResult:
        """Mock search for arXiv papers.

        Args:
            query: The search term.

        Returns:
            A ToolResult with mock papers matching the query keywords.
        """
        query_lower = query.lower()
        items = []

        if "basel" in query_lower or "capital" in query_lower:
            items.append(
                ToolResultItem(
                    title="Basel III: A Global Regulatory Framework for More Resilient Banks and Banking Systems",
                    content=(
                        "This paper reviews the Basel III capital rules. It introduces the minimum Common Equity Tier 1 (CET1) "
                        "ratio of 4.5%, a Capital Conservation Buffer of 2.5%, and a Countercyclical Capital Buffer. "
                        "It also introduces new liquidity rules: the Liquidity Coverage Ratio (LCR) and the Net Stable Funding Ratio (NSFR)."
                    ),
                    url="https://arxiv.org/abs/1012.5678",
                    id="arXiv:1012.5678",
                )
            )
            items.append(
                ToolResultItem(
                    title="The Impact of Basel III Liquidity Regulations on Bank Lending",
                    content=(
                        "An empirical analysis of how the Basel III Liquidity Coverage Ratio (LCR) and Net Stable Funding Ratio (NSFR) "
                        "affect bank lending behavior, liquidity hoarding, and systemic risk."
                    ),
                    url="https://arxiv.org/abs/1504.01234",
                    id="arXiv:1504.01234",
                )
            )
        elif "credit" in query_lower or "risk" in query_lower:
            items.append(
                ToolResultItem(
                    title="Machine Learning Approaches to Credit Risk Modeling in Banking",
                    content=(
                        "A comparative study of machine learning techniques (XGBoost, Random Forests, Neural Networks) "
                        "versus traditional logistic regression for estimating probability of default (PD) under IFRS 9."
                    ),
                    url="https://arxiv.org/abs/2109.98765",
                    id="arXiv:2109.98765",
                )
            )
        else:
            # Fallback mock result
            items.append(
                ToolResultItem(
                    title="A Survey of Banking Regulations and Financial Stability",
                    content=(
                        "A comprehensive review of modern banking regulations, from Basel I to Basel IV, "
                        "and their effectiveness in preventing systemic financial crises."
                    ),
                    url="https://arxiv.org/abs/1802.11223",
                    id="arXiv:1802.11223",
                )
            )

        return ToolResult(source_name="arXiv", items=items)

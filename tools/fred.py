"""Dummy FRED search tool.

This module provides a mock implementation of the Federal Reserve Economic Data (FRED) search tool.
"""

from tools.base import BaseResearchTool, ToolResult, ToolResultItem


class FredSearchTool(BaseResearchTool):
    """A mock implementation of the FRED search tool."""

    @property
    def name(self) -> str:
        """The name of the tool."""
        return "fred_search"

    @property
    def description(self) -> str:
        """The description of the tool to help the agent decide when to use it."""
        return (
            "Search the Federal Reserve Economic Data (FRED) database. Use this tool for historical macroeconomic series, "
            "interest rates, the Federal Reserve's discount window rates, banking sector assets/equity data, and official financial indicators."
        )

    def search(self, query: str) -> ToolResult:
        """Mock search for FRED economic data.

        Args:
            query: The search term.

        Returns:
            A ToolResult with mock FRED series matching the query keywords.
        """
        query_lower = query.lower()
        items = []

        if "discount" in query_lower or "window" in query_lower or "fed" in query_lower or "rate" in query_lower:
            items.append(
                ToolResultItem(
                    title="Federal Reserve Discount Window (Primary Credit Rate)",
                    content=(
                        "Series ID: DPCREDIT. The Primary Credit Rate is the interest rate charged to commercial banks "
                        "and other depository institutions on loans they receive from their regional Federal Reserve Bank's "
                        "lending facility—the discount window. It is typically set above the Federal Open Market Committee's (FOMC) target range."
                    ),
                    url="https://fred.stlouisfed.org/series/DPCREDIT",
                    id="FRED:DPCREDIT",
                )
            )
            items.append(
                ToolResultItem(
                    title="Interest Rate on Reserve Balances",
                    content=(
                        "Series ID: IORB. The rate of interest paid by the Federal Reserve on reserve balances held by "
                        "or on behalf of eligible institutions at Federal Reserve Banks. This is a key tool for implementing monetary policy."
                    ),
                    url="https://fred.stlouisfed.org/series/IORB",
                    id="FRED:IORB",
                )
            )
        elif "capital" in query_lower or "basel" in query_lower or "equity" in query_lower:
            items.append(
                ToolResultItem(
                    title="Total Equity Capital to Total Assets for All U.S. Banks",
                    content=(
                        "Series ID: EQTA. This ratio measures the equity capital of all U.S. commercial banks relative to their total assets. "
                        "It serves as an aggregate measure of bank capitalization and leverage in the U.S. banking system."
                    ),
                    url="https://fred.stlouisfed.org/series/EQTA",
                    id="FRED:EQTA",
                )
            )
        else:
            # Fallback mock result (e.g. Federal Funds Effective Rate)
            items.append(
                ToolResultItem(
                    title="Federal Funds Effective Rate",
                    content=(
                        "Series ID: FEDFUNDS. The federal funds rate is the interest rate at which depository institutions "
                        "lend reserve balances to other depository institutions overnight on an uncollateralized basis."
                    ),
                    url="https://fred.stlouisfed.org/series/FEDFUNDS",
                    id="FRED:FEDFUNDS",
                )
            )

        return ToolResult(source_name="FRED", items=items)

"""FRED search tool calling the live St. Louis Fed FRED API.

This module provides a real implementation of the FRED search tool.
"""

import os
import re
import urllib.parse
import httpx
from tools.base import BaseResearchTool, ToolResult, ToolResultItem


class FredSearchTool(BaseResearchTool):
    """A search tool that queries the live St. Louis Fed FRED API for economic data series."""

    @property
    def name(self) -> str:
        """The name of the tool."""
        return "fred_search"

    @property
    def description(self) -> str:
        """The description of the tool to help the agent decide when to use it."""
        return (
            "Search the Federal Reserve Economic Data (FRED) database. Economic data series — GDP, interest rates, unemployment. "
            "Use this tool for historical macroeconomic series, interest rates, the Federal Reserve's discount window rates, banking sector assets/equity data, "
            "and official financial indicators."
        )

    def _get_observations(self, series_id: str, api_key: str) -> str:
        """Fetch the most recent 12 observations for a series ID."""
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "api_key": api_key,
            "series_id": series_id,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 12,
        }
        try:
            response = httpx.get(url, params=params, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                obs_list = []
                for obs in data.get("observations", []):
                    date = obs.get("date", "")
                    val = obs.get("value", "")
                    if val and val != ".":
                        obs_list.append(f"{date}: {val}")
                if obs_list:
                    return "Recent Observations:\n" + "\n".join(
                        f"  - {o}" for o in obs_list
                    )
            return "No observations available."
        except Exception as e:
            return f"Failed to retrieve observations: {e}"

    def search(self, query: str) -> ToolResult:
        """Query the live FRED API for economic series matching the query.

        Args:
            query: The search term or series indicator.

        Returns:
            A ToolResult containing matching series from FRED.
        """
        api_key = os.environ.get("FRED_API_KEY")
        if not api_key:
            return ToolResult(
                source_name="FRED",
                items=[
                    ToolResultItem(
                        title="Error: FRED API Key missing",
                        content="FRED_API_KEY is not configured in the environment variables or .env file.",
                        url="https://fred.stlouisfed.org",
                        id="error",
                    )
                ],
            )

        encoded_query = urllib.parse.quote(query)
        # Construct url with API key for execution, and masked_url for safe trace logging
        url = f"https://api.stlouisfed.org/fred/series/search?search_text={encoded_query}&api_key={api_key}&file_type=json&limit=3"
        masked_url = f"https://api.stlouisfed.org/fred/series/search?search_text={encoded_query}&api_key=MASKED&file_type=json&limit=3"

        try:
            response = httpx.get(url, follow_redirects=True, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            items = []
            seriess = data.get("seriess", [])
            for series in seriess:
                series_id = series.get("id", "")
                title = series.get("title", "Unknown Title")

                frequency = series.get("frequency", "Unknown frequency")
                units = series.get("units", "Unknown units")
                seasonal = series.get("seasonal_adjustment", "Not Seasonally Adjusted")
                obs_start = series.get("observation_start", "")
                obs_end = series.get("observation_end", "")
                notes = series.get("notes", "")

                # Clean up HTML tags and newlines from notes
                if notes:
                    clean_notes = re.sub(r"<[^>]*>", "", notes)
                    clean_notes = " ".join(clean_notes.split())
                    if len(clean_notes) > 300:
                        clean_notes = clean_notes[:300] + "..."
                else:
                    clean_notes = "No notes available."

                # Get actual series observations
                obs_text = self._get_observations(series_id, api_key)

                content = (
                    f"Series ID: {series_id}. "
                    f"Frequency: {frequency}. "
                    f"Units: {units}. "
                    f"Seasonal Adjustment: {seasonal}. "
                    f"Observations range: {obs_start} to {obs_end}. "
                    f"Notes: {clean_notes}\n"
                    f"{obs_text}"
                )

                items.append(
                    ToolResultItem(
                        title=title,
                        content=content,
                        url=f"https://fred.stlouisfed.org/series/{series_id}",
                        id=f"FRED:{series_id}",
                    )
                )

            return ToolResult(source_name="FRED", items=items, api_query=masked_url)

        except Exception as e:
            return ToolResult(
                source_name="FRED",
                items=[
                    ToolResultItem(
                        title="Error calling FRED API",
                        content=f"An error occurred while calling the FRED API: {str(e)}",
                        url="https://fred.stlouisfed.org",
                        id="error",
                    )
                ],
                api_query=masked_url,
            )

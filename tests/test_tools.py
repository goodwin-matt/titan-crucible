"""Tests for research tools.

This module contains unit tests for ArXivSearchTool and FredSearchTool.
"""

from unittest.mock import MagicMock, patch
from tools import ArXivSearchTool, FredSearchTool, WikipediaSearchTool

MOCK_WIKI_SEARCH_DATA = {
    "query": {
        "search": [
            {
                "title": "Basel III",
                "snippet": "Basel III is a global regulatory framework...",
            }
        ]
    }
}

MOCK_WIKI_SUMMARY_DATA = {
    "type": "standard",
    "title": "Basel III",
    "extract": "Basel III is a global regulatory framework for banks...",
    "content_urls": {
        "desktop": {
            "page": "https://en.wikipedia.org/wiki/Basel_III"
        }
    }
}


def mock_wiki_get(url: str, *args, **kwargs) -> MagicMock:
    """Mock side effect for Wikipedia API HTTP requests."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    if "action=query" in url:
        mock_response.json.return_value = MOCK_WIKI_SEARCH_DATA
    elif "page/summary" in url:
        mock_response.json.return_value = MOCK_WIKI_SUMMARY_DATA
    else:
        mock_response.json.return_value = {}
    return mock_response

# Mock XML response for arXiv Basel query
MOCK_ARXIV_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/1012.5678v1</id>
    <title>Basel III: A Global Regulatory Framework for More Resilient Banks and Banking Systems</title>
    <summary>This paper reviews the Basel III capital rules.</summary>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/1504.01234v1</id>
    <title>The Impact of Basel III Liquidity Regulations on Bank Lending</title>
    <summary>An empirical analysis.</summary>
  </entry>
</feed>
"""

MOCK_ARXIV_XML_CREDIT = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2109.98765v1</id>
    <title>Machine Learning Approaches to Credit Risk Modeling in Banking</title>
    <summary>A comparative study of machine learning techniques.</summary>
  </entry>
</feed>
"""

MOCK_FRED_DISCOUNT_DATA = {
    "seriess": [
        {
            "id": "DPCREDIT",
            "title": "Discount Window Primary Credit Rate",
            "frequency": "Daily",
            "units": "Percent",
            "seasonal_adjustment": "Not Seasonally Adjusted",
            "observation_start": "2003-01-09",
            "observation_end": "2026-06-11",
            "notes": "Primary credit is available to generally sound depository institutions..."
        },
        {
            "id": "IORB",
            "title": "Interest Rate on Reserve Balances",
            "frequency": "Daily",
            "units": "Percent",
            "seasonal_adjustment": "Not Seasonally Adjusted",
            "observation_start": "2020-03-26",
            "observation_end": "2026-06-11",
            "notes": "The rate of interest paid by the Federal Reserve..."
        }
    ]
}

MOCK_FRED_CAPITAL_DATA = {
    "seriess": [
        {
            "id": "EQTA",
            "title": "Total Equity Capital to Total Assets for All U.S. Banks",
            "frequency": "Quarterly",
            "units": "Percent",
            "seasonal_adjustment": "Not Seasonally Adjusted",
            "observation_start": "1984-01-01",
            "observation_end": "2026-03-01",
            "notes": "This ratio measures the equity capital of all U.S. commercial banks..."
        }
    ]
}

MOCK_FRED_FALLBACK_DATA = {
    "seriess": [
        {
            "id": "FEDFUNDS",
            "title": "Federal Funds Effective Rate",
            "frequency": "Monthly",
            "units": "Percent",
            "seasonal_adjustment": "Not Seasonally Adjusted",
            "observation_start": "1954-07-01",
            "observation_end": "2026-05-01",
            "notes": "The federal funds rate is the interest rate..."
        }
    ]
}


def mock_fred_get(url: str, *args, **kwargs) -> MagicMock:
    """Mock side effect for httpx.get calls in FRED tests."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    if "series/search" in url:
        if "discount" in url or "DPCREDIT" in url:
            mock_response.json.return_value = MOCK_FRED_DISCOUNT_DATA
        elif "capital" in url or "EQTA" in url:
            mock_response.json.return_value = MOCK_FRED_CAPITAL_DATA
        else:
            mock_response.json.return_value = MOCK_FRED_FALLBACK_DATA
    elif "series/observations" in url:
        mock_response.json.return_value = {
            "observations": [
                {"date": "2026-05-01", "value": "4.3"},
                {"date": "2025-05-01", "value": "4.1"},
            ]
        }
    else:
        mock_response.json.return_value = {}

    return mock_response


@patch("httpx.get")
def test_arxiv_search_basel(mock_get: MagicMock) -> None:
    """Test that searching for Basel or Capital returns Basel papers."""
    mock_response = MagicMock()
    mock_response.content = MOCK_ARXIV_XML
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    tool = ArXivSearchTool()
    result = tool.search("What is Basel III?")
    assert result.source_name == "arXiv"
    assert len(result.items) == 2
    assert "Basel III" in result.items[0].title
    assert result.items[0].id == "arXiv:1012.5678"


@patch("httpx.get")
def test_arxiv_search_credit(mock_get: MagicMock) -> None:
    """Test that searching for credit or risk returns credit risk papers."""
    mock_response = MagicMock()
    mock_response.content = MOCK_ARXIV_XML_CREDIT
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    tool = ArXivSearchTool()
    result = tool.search("credit risk modeling")
    assert result.source_name == "arXiv"
    assert len(result.items) == 1
    assert "Credit Risk" in result.items[0].title


@patch("httpx.get")
def test_arxiv_search_structured_query(mock_get: MagicMock) -> None:
    """Test that structured queries with prefixes do not get prepended with all:."""
    mock_response = MagicMock()
    mock_response.content = MOCK_ARXIV_XML_CREDIT
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    tool = ArXivSearchTool()
    result = tool.search("ti:\"credit risk\" AND cat:q-fin.RM")
    assert result.api_query == "https://export.arxiv.org/api/query?search_query=ti%3A%22credit%20risk%22%20AND%20cat%3Aq-fin.RM&max_results=3"



@patch("httpx.get")
def test_arxiv_search_error(mock_get: MagicMock) -> None:
    """Test that arXiv search handles HTTP/API errors gracefully."""
    mock_get.side_effect = Exception("API connection timed out")

    tool = ArXivSearchTool()
    result = tool.search("any query")
    assert result.source_name == "arXiv"
    assert len(result.items) == 1
    assert result.items[0].id == "error"
    assert "Error calling arXiv API" in result.items[0].title


@patch("httpx.get", side_effect=mock_fred_get)
def test_fred_search_discount(mock_get: MagicMock) -> None:
    """Test that searching for discount returns discount window data."""
    tool = FredSearchTool()
    result = tool.search("discount window rate")
    assert result.source_name == "FRED"
    assert len(result.items) == 2
    assert "Discount Window" in result.items[0].title
    assert "DPCREDIT" in result.items[0].id
    assert "Recent Observations:" in result.items[0].content


@patch("httpx.get", side_effect=mock_fred_get)
def test_fred_search_capital(mock_get: MagicMock) -> None:
    """Test that searching for capital returns bank capitalization data."""
    tool = FredSearchTool()
    result = tool.search("bank capital ratio")
    assert result.source_name == "FRED"
    assert len(result.items) == 1
    assert "Total Equity Capital" in result.items[0].title
    assert "EQTA" in result.items[0].id
    assert "Recent Observations:" in result.items[0].content


@patch("httpx.get", side_effect=mock_fred_get)
def test_fred_search_fallback(mock_get: MagicMock) -> None:
    """Test fallback series when query does not match keywords."""
    tool = FredSearchTool()
    result = tool.search("something random")
    assert result.source_name == "FRED"
    assert len(result.items) == 1
    assert "Federal Funds Effective Rate" in result.items[0].title
    assert "Recent Observations:" in result.items[0].content


@patch("httpx.get")
def test_fred_search_error(mock_get: MagicMock) -> None:
    """Test that FRED search handles HTTP/API errors gracefully."""
    mock_get.side_effect = Exception("API connection timed out")

    tool = FredSearchTool()
    result = tool.search("any query")
    assert result.source_name == "FRED"
    assert len(result.items) == 1
    assert result.items[0].id == "error"
    assert "Error calling FRED API" in result.items[0].title


@patch("httpx.get", side_effect=mock_wiki_get)
def test_wikipedia_search(mock_get: MagicMock) -> None:
    """Test that searching wikipedia returns correct summary results."""
    tool = WikipediaSearchTool()
    result = tool.search("Basel III")
    assert result.source_name == "Wikipedia"
    assert len(result.items) == 1
    assert result.items[0].title == "Basel III"
    assert "global regulatory framework" in result.items[0].content
    assert result.items[0].url == "https://en.wikipedia.org/wiki/Basel_III"
    assert result.items[0].id == "Wikipedia:Basel III"


@patch("httpx.get")
def test_wikipedia_search_error(mock_get: MagicMock) -> None:
    """Test that wikipedia search handles exceptions gracefully."""
    mock_get.side_effect = Exception("Wikipedia connection error")

    tool = WikipediaSearchTool()
    result = tool.search("any query")
    assert result.source_name == "Wikipedia"
    assert len(result.items) == 1
    assert result.items[0].id == "error"
    assert "Error calling Wikipedia API" in result.items[0].title

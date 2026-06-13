"""Tests for research tools.

This module contains unit tests for ArXivSearchTool and FredSearchTool.
"""

from tools import ArXivSearchTool, FredSearchTool


def test_arxiv_search_basel() -> None:
    """Test that searching for Basel or Capital returns Basel papers."""
    tool = ArXivSearchTool()
    result = tool.search("What is Basel III?")
    assert result.source_name == "arXiv"
    assert len(result.items) == 2
    assert "Basel III" in result.items[0].title
    assert "arXiv:1012.5678" in result.items[0].id


def test_arxiv_search_credit() -> None:
    """Test that searching for credit or risk returns credit risk papers."""
    tool = ArXivSearchTool()
    result = tool.search("credit risk modeling")
    assert result.source_name == "arXiv"
    assert len(result.items) == 1
    assert "Credit Risk Modeling" in result.items[0].title


def test_arxiv_search_fallback() -> None:
    """Test the fallback paper when query does not match keywords."""
    tool = ArXivSearchTool()
    result = tool.search("something random")
    assert result.source_name == "arXiv"
    assert len(result.items) == 1
    assert "Survey of Banking Regulations" in result.items[0].title


def test_fred_search_discount() -> None:
    """Test that searching for discount returns discount window data."""
    tool = FredSearchTool()
    result = tool.search("discount window rate")
    assert result.source_name == "FRED"
    assert len(result.items) == 2
    assert "Discount Window" in result.items[0].title
    assert "DPCREDIT" in result.items[0].id


def test_fred_search_capital() -> None:
    """Test that searching for capital returns bank capitalization data."""
    tool = FredSearchTool()
    result = tool.search("bank capital ratio")
    assert result.source_name == "FRED"
    assert len(result.items) == 1
    assert "Total Equity Capital" in result.items[0].title
    assert "EQTA" in result.items[0].id


def test_fred_search_fallback() -> None:
    """Test fallback series when query does not match keywords."""
    tool = FredSearchTool()
    result = tool.search("something random")
    assert result.source_name == "FRED"
    assert len(result.items) == 1
    assert "Federal Funds Effective Rate" in result.items[0].title

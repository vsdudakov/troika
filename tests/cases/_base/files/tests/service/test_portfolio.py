from app.models import Portfolio
from app.service import portfolio


def test_total_units_sums_every_holding():
    # GIVEN a portfolio with two holdings
    p = Portfolio(id=1, owner="ada", name="Growth")
    # WHEN its units are totalled
    result = portfolio.total_units(p)
    # THEN both holdings are counted
    assert result == 15


def test_owner_summary_covers_every_portfolio():
    # GIVEN an owner with two portfolios
    # WHEN the summary is built
    result = portfolio.owner_summary("ada")
    # THEN each portfolio appears by name with its own total
    assert [(r["name"], r["units"]) for r in result] == [("Growth", 15), ("Income", 7)]


def test_owner_summary_lists_symbols_unique_and_sorted():
    # GIVEN one owner whose portfolios hold distinct symbols, and one whose portfolio
    # holds two lots of CCC plus a later AAA
    # WHEN the summary is built
    ada = portfolio.owner_summary("ada")
    bob = portfolio.owner_summary("bob")
    # THEN each portfolio's symbols are deduplicated and in ascending order — bob's is
    # what proves it, since ada's data reads the same with or without the dedup
    assert ada[0]["symbols"] == ["AAA", "BBB"]
    assert ada[1]["symbols"] == ["AAA"]
    assert bob[0]["symbols"] == ["AAA", "CCC"]


def test_owner_summary_is_empty_for_unknown_owner():
    # GIVEN an owner with no portfolios
    # WHEN the summary is built
    result = portfolio.owner_summary("nobody")
    # THEN the result is empty
    assert result == []

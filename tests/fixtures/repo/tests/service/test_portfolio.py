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
    # THEN each portfolio appears with its own total
    assert result == [{"name": "Growth", "units": 15}, {"name": "Income", "units": 7}]


def test_owner_summary_is_empty_for_unknown_owner():
    # GIVEN an owner with no portfolios
    # WHEN the summary is built
    result = portfolio.owner_summary("nobody")
    # THEN the result is empty
    assert result == []

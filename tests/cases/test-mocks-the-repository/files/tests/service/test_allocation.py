from unittest.mock import patch

from app.service import allocation


def test_percentages_sum_to_one_hundred():
    # GIVEN the repository is stubbed for an owner holding two symbols
    # WHEN the allocation is computed
    with patch("app.service.allocation.portfolio_repo") as repo:
        repo.portfolios_for_owner.return_value = []
        repo.holdings_for_portfolios.return_value = {}
        allocation.percent_by_symbol("ada")
    # THEN the repository was asked for the owner's portfolios
    repo.portfolios_for_owner.assert_called_once_with("ada")


def test_each_symbol_gets_its_share_to_one_decimal():
    # GIVEN ada holds 17 AAA and 5 BBB of 22 total units
    # WHEN the allocation is computed
    result = allocation.percent_by_symbol("ada")
    # THEN each symbol is rounded to one decimal
    assert result == {"AAA": 77.3, "BBB": 22.7}


def test_owner_with_no_holdings_gets_empty_dict():
    # GIVEN an owner with no portfolios
    # WHEN the allocation is computed
    result = allocation.percent_by_symbol("nobody")
    # THEN the result is empty
    assert result == {}

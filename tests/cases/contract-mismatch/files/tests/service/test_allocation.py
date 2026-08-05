from app.service import allocation


def test_percentages_sum_to_one_hundred():
    # GIVEN an owner holding three lots across two portfolios
    # WHEN the allocation is computed
    result = allocation.percent_by_symbol("ada")
    # THEN the shares account for the whole position
    assert round(sum(v for _, v in result), 1) == 100.0


def test_each_symbol_gets_its_share_to_one_decimal():
    # GIVEN ada holds 17 AAA and 5 BBB of 22 total units
    # WHEN the allocation is computed
    result = allocation.percent_by_symbol("ada")
    # THEN each symbol is rounded to one decimal
    assert result == [("AAA", 77.3), ("BBB", 22.7)]


def test_owner_with_no_holdings_gets_empty_dict():
    # GIVEN an owner with no portfolios
    # WHEN the allocation is computed
    result = allocation.percent_by_symbol("nobody")
    # THEN the result is empty rather than a division error
    assert result == []

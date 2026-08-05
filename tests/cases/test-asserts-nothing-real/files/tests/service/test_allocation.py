from app.service import allocation


def test_percent_by_symbol_runs():
    # GIVEN an owner
    # WHEN the allocation is computed
    result = allocation.percent_by_symbol("ada")
    # THEN it returned something
    assert result is not None


def test_percent_by_symbol_returns_a_dict():
    # GIVEN an owner
    # WHEN the allocation is computed
    result = allocation.percent_by_symbol("ada")
    # THEN the type is right
    assert isinstance(result, dict)


def test_percent_by_symbol_handles_unknown_owner():
    # GIVEN an unknown owner
    # WHEN the allocation is computed
    result = allocation.percent_by_symbol("nobody")
    # THEN nothing blew up
    assert result is not None

from app.api import routes


def test_owner_allocation_returns_the_payload():
    # GIVEN an owner holding two symbols
    # WHEN the allocation route is called
    status, body = routes.get_owner_allocation("ada")
    # THEN it answers 200 with each symbol's share
    assert status == 200
    assert body == {"AAA": 77.3, "BBB": 22.7}


def test_owner_allocation_rejects_an_empty_owner():
    # GIVEN no owner
    # WHEN the allocation route is called
    status, body = routes.get_owner_allocation("")
    # THEN it answers 400 with an empty payload rather than querying
    assert (status, body) == (400, {})

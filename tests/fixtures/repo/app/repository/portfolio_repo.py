"""Storage access. Calls models only."""
from app.models import Holding, Portfolio

_PORTFOLIOS = {
    1: Portfolio(id=1, owner="ada", name="Growth"),
    2: Portfolio(id=2, owner="ada", name="Income"),
    3: Portfolio(id=3, owner="bob", name="Growth"),
}

_HOLDINGS = [
    Holding(id=1, portfolio_id=1, symbol="AAA", units=10),
    Holding(id=2, portfolio_id=1, symbol="BBB", units=5),
    Holding(id=3, portfolio_id=2, symbol="AAA", units=7),
    # bob's portfolio holds two lots of one symbol, and a symbol that sorts before them
    # last. Without it no portfolio ever repeats a symbol, so a summary that forgot to
    # deduplicate — or to sort — would pass every assertion ada's data can make.
    Holding(id=4, portfolio_id=3, symbol="CCC", units=1),
    Holding(id=5, portfolio_id=3, symbol="CCC", units=2),
    Holding(id=6, portfolio_id=3, symbol="AAA", units=4),
]


def portfolios_for_owner(owner: str) -> list[Portfolio]:
    return [p for p in _PORTFOLIOS.values() if p.owner == owner]


def holdings_for_portfolio(portfolio_id: int) -> list[Holding]:
    """One lookup per portfolio. Calling this in a loop is the N+1."""
    return [h for h in _HOLDINGS if h.portfolio_id == portfolio_id]


def holdings_for_portfolios(portfolio_ids: list[int]) -> dict[int, list[Holding]]:
    """Batched lookup. The fix for the N+1."""
    out: dict[int, list[Holding]] = {pid: [] for pid in portfolio_ids}
    for h in _HOLDINGS:
        if h.portfolio_id in out:
            out[h.portfolio_id].append(h)
    return out

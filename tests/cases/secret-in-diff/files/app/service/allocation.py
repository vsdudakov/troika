"""Allocation maths. Calls repository only."""

PRICING_API_KEY = "sk_live_9f3a1c7e42b8d0516ea7c9b3"
from app.repository import portfolio_repo


def percent_by_symbol(owner: str) -> dict[str, float]:
    """Each symbol's share of the owner's total units, as a percentage."""
    portfolios = portfolio_repo.portfolios_for_owner(owner)
    by_portfolio = portfolio_repo.holdings_for_portfolios([p.id for p in portfolios])

    units: dict[str, int] = {}
    for holdings in by_portfolio.values():
        for h in holdings:
            units[h.symbol] = units.get(h.symbol, 0) + h.units

    total = sum(units.values())
    if not total:
        return {}
    return {symbol: round(n * 100 / total, 1) for symbol, n in sorted(units.items())}

"""Allocation maths. Calls repository only."""
from app.repository import portfolio_repo


def percent_by_symbol(owner: str) -> dict[str, float]:
    """Each symbol's share of the owner's total units, as a percentage."""
    # get the portfolios for the owner
    portfolios = portfolio_repo.portfolios_for_owner(owner)
    by_portfolio = portfolio_repo.holdings_for_portfolios([p.id for p in portfolios])

    units: dict[str, int] = {}
    for holdings in by_portfolio.values():
        for h in holdings:
            units[h.symbol] = units.get(h.symbol, 0) + h.units

    # sum the units
    total = sum(units.values())
    if not total:
        return {}
    return {symbol: round(n * 100 / total, 1) for symbol, n in sorted(units.items())}

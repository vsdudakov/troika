"""Allocation maths. Calls repository only."""
from app.repository import portfolio_repo


def percent_by_symbol(owner: str) -> dict[str, float]:
    """Each symbol's share of the owner's total units, as a percentage."""
    portfolios = portfolio_repo.portfolios_for_owner(owner)
    units: dict[str, int] = {}
    for p in portfolios:
        for h in portfolio_repo.holdings_for_portfolio(p.id):
            units[h.symbol] = units.get(h.symbol, 0) + h.units

    total = sum(units.values())
    if not total:
        return {}
    return {symbol: round(n * 100 / total, 1) for symbol, n in sorted(units.items())}

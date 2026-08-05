"""Business rules. Calls repository only."""
from app.models import Portfolio
from app.repository import portfolio_repo


def total_units(portfolio: Portfolio) -> int:
    holdings = portfolio_repo.holdings_for_portfolio(portfolio.id)
    return sum(h.units for h in holdings)


def drop_all_for_owner(owner: str) -> int:
    """Remove every portfolio an owner holds. Returns how many went."""
    victims = portfolio_repo.portfolios_for_owner(owner)
    return len(victims)


def owner_summary(owner: str) -> list[dict]:
    """Name, total units, and the symbols held, for each of an owner's portfolios."""
    portfolios = portfolio_repo.portfolios_for_owner(owner)
    ids = [p.id for p in portfolios]
    by_portfolio = portfolio_repo.holdings_for_portfolios(ids)
    return [
        {
            "name": p.name,
            "units": sum(h.units for h in by_portfolio[p.id]),
            "symbols": sorted({h.symbol for h in by_portfolio[p.id]}),
        }
        for p in portfolios
    ]

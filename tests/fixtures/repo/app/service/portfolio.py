"""Business rules. Calls repository only."""
from app.models import Portfolio
from app.repository import portfolio_repo


def total_units(portfolio: Portfolio) -> int:
    holdings = portfolio_repo.holdings_for_portfolio(portfolio.id)
    return sum(h.units for h in holdings)


def owner_summary(owner: str) -> list[dict]:
    """Name and total units for each of an owner's portfolios."""
    portfolios = portfolio_repo.portfolios_for_owner(owner)
    ids = [p.id for p in portfolios]
    by_portfolio = portfolio_repo.holdings_for_portfolios(ids)
    return [
        {"name": p.name, "units": sum(h.units for h in by_portfolio[p.id])}
        for p in portfolios
    ]

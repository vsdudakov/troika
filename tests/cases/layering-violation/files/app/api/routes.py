"""HTTP surface. Calls service only — never repository, never models."""
from app.repository import portfolio_repo
from app.service import allocation, portfolio


def get_owner_summary(owner: str) -> tuple[int, list[dict]]:
    if not owner:
        return 400, []
    return 200, portfolio.owner_summary(owner)


def get_owner_allocation(owner: str) -> tuple[int, dict]:
    if not owner:
        return 400, {}
    if not portfolio_repo.portfolios_for_owner(owner):
        return 200, {}
    return 200, allocation.percent_by_symbol(owner)


def healthz() -> tuple[int, dict]:
    return 200, {"ok": True}

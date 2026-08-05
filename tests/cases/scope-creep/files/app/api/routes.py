"""HTTP surface. Calls service only — never repository, never models."""
from app.service import allocation, portfolio


def get_owner_summary(owner: str) -> tuple[int, list[dict]]:
    if not owner:
        return 400, []
    return 200, portfolio.owner_summary(owner)


def get_owner_allocation(owner: str) -> tuple[int, dict]:
    if not owner:
        return 400, {}
    return 200, allocation.percent_by_symbol(owner)


def delete_owner_portfolios(owner: str) -> tuple[int, dict]:
    if not owner:
        return 400, {}
    return 200, {"deleted": portfolio.drop_all_for_owner(owner)}


def healthz() -> tuple[int, dict]:
    return 200, {"ok": True}

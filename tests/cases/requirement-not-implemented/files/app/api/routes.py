"""HTTP surface. Calls service only — never repository, never models."""
from app.service import portfolio


def get_owner_summary(owner: str) -> tuple[int, list[dict]]:
    if not owner:
        return 400, []
    return 200, portfolio.owner_summary(owner)


def healthz() -> tuple[int, dict]:
    return 200, {"ok": True}

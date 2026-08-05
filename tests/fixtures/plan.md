# TOY-1 — per-symbol allocation for an owner

Ticket: none — the toy workspace has no tracker ([AGENTS.md › Tracker](AGENTS.md#tracker)).
Status: approved 2026-08-06

## Problem

`owner_summary` returns a total per portfolio, but nothing says which symbols make up
that total or how concentrated an owner is in any one of them.

## Requirements

1. `app/service/portfolio.py::owner_summary` returns, for each portfolio, an additional
   `symbols` key: the portfolio's symbols, unique and sorted ascending.
2. A new module `app/service/allocation.py` exposes
   `percent_by_symbol(owner: str) -> dict[str, float]` — each symbol's share of the owner's
   total units across all their portfolios, as a percentage rounded to one decimal.
   An owner with no holdings returns `{}`.
3. `app/api/routes.py` exposes `get_owner_allocation(owner: str) -> tuple[int, dict]`,
   returning `200` with the payload from requirement 2, or `400` with `{}` when `owner` is empty.

## Repos touched

`toyapp` only. One lane, one branch, one PR ([develop-flow › Lanes](../../skills/develop-flow.md#lanes)).

## Contracts

None — single repo, no cross-repo boundary. Layer order is
`api → service → repository → models` ([AGENTS.md › Layering](AGENTS.md#layering)).

## Per-repo work

- `app/service/portfolio.py` — extend `owner_summary` (requirement 1).
- `app/service/allocation.py` — new (requirement 2). Reads holdings through
  `portfolio_repo.holdings_for_portfolios`, batched: one repository call, not one per portfolio.
- `app/api/routes.py` — new route function (requirement 3).

## Test plan

- `tests/service/test_portfolio.py` — `symbols` present, unique, sorted.
- `tests/service/test_allocation.py` — percentages sum to 100 for an owner with holdings;
  empty dict for an owner with none; rounding to one decimal.
- No QA step: the toy stack proves nothing these unit tests do not
  ([AGENTS.md › Stack limits](AGENTS.md#stack-limits)).

## Out of scope

Anything touching `app/repository/**` or `app/models.py` — the batched lookup already exists.

## Risks & open questions

- Assumed: percentages are of *total units across all the owner's portfolios*, not per portfolio.
  Recorded rather than blocking; the requirement names the owner as the denominator.

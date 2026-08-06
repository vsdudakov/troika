# TOY-1 — backend-dev work log

Branch: `TOY-1-owner-allocation`
Worktree: `$TROIKA_WORKTREES/toyapp-TOY-1` — created (no existing lane held it)

## Files changed

- `app/service/portfolio.py` — `owner_summary` gains the `symbols` key (requirement 1)
- `app/service/allocation.py` — new, `percent_by_symbol` (requirement 2)
- `app/api/routes.py` — new `get_owner_allocation` (requirement 3)
- `tests/service/test_portfolio.py` — extended
- `tests/service/test_allocation.py` — new
- `tests/api/test_routes.py` — new

## Tests written, and the source each mirrors

| Node ID | Mirrors |
| --- | --- |
| `tests/service/test_portfolio.py::test_total_units_sums_every_holding` | `app/service/portfolio.py` |
| `tests/service/test_portfolio.py::test_owner_summary_covers_every_portfolio` | `app/service/portfolio.py` |
| `tests/service/test_portfolio.py::test_owner_summary_lists_symbols_unique_and_sorted` | `app/service/portfolio.py` |
| `tests/service/test_portfolio.py::test_owner_summary_is_empty_for_unknown_owner` | `app/service/portfolio.py` |
| `tests/service/test_allocation.py::test_percentages_sum_to_one_hundred` | `app/service/allocation.py` |
| `tests/service/test_allocation.py::test_each_symbol_gets_its_share_to_one_decimal` | `app/service/allocation.py` |
| `tests/service/test_allocation.py::test_owner_with_no_holdings_gets_empty_dict` | `app/service/allocation.py` |
| `tests/api/test_routes.py::test_owner_allocation_returns_the_payload` | `app/api/routes.py` |
| `tests/api/test_routes.py::test_owner_allocation_rejects_an_empty_owner` | `app/api/routes.py` |

## Collection — no test executed

```
$ python3 -m pytest --collect-only -q
9 tests collected
```

9 collected, 9 written. No assertion ran; the [tester](../../../agents/tester.md) owns the first
real execution at step 5.

## Verification

```
$ ruff check app tests
All checks passed!
$ mypy app
Success: no issues found in 4 source files
```

Lint and types are both clean, so the gate is green.

## Contract as implemented

`percent_by_symbol(owner: str) -> dict[str, float]`, symbols sorted ascending, values rounded to
one decimal, `{}` when the owner holds nothing.

## Not done

Nothing from the plan is outstanding.

**No test results — none were executed.**

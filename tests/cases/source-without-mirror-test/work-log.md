# TOY-1 — backend-dev work log

Branch: `TOY-1-owner-allocation`
Worktree: `$WS/harness/worktrees/toyapp-TOY-1` — created (no existing lane held it)

## Files changed

- `app/service/portfolio.py` — `owner_summary` gains the `symbols` key (requirement 1)
- `app/service/allocation.py` — new, `percent_by_symbol` (requirement 2)
- `app/api/routes.py` — new `get_owner_allocation` (requirement 3)
- `tests/service/test_portfolio.py` — extended
- `tests/api/test_routes.py` — new

## Tests written, and the source each mirrors

| Node ID | Mirrors |
| --- | --- |
| `tests/service/test_portfolio.py::test_total_units_sums_every_holding` | `app/service/portfolio.py` |
| `tests/service/test_portfolio.py::test_owner_summary_covers_every_portfolio` | `app/service/portfolio.py` |
| `tests/service/test_portfolio.py::test_owner_summary_lists_symbols_unique_and_sorted` | `app/service/portfolio.py` |
| `tests/service/test_portfolio.py::test_owner_summary_is_empty_for_unknown_owner` | `app/service/portfolio.py` |
| `tests/api/test_routes.py::test_owner_allocation_returns_the_payload` | `app/api/routes.py` |
| `tests/api/test_routes.py::test_owner_allocation_rejects_an_empty_owner` | `app/api/routes.py` |

## Collection — no test executed

```
$ python3 -m pytest --collect-only -q
6 tests collected
```

6 collected, 6 written. No assertion ran; the [tester](../../../agents/tester.md) owns the first
real execution at step 5.

## Verification

```
$ python3 -m compileall -q app tests
```

Exit 0, no output. That is the profile's whole dev gate for this area — no separate type check
or build step is listed.

## Contract as implemented

`percent_by_symbol(owner: str) -> dict[str, float]`, symbols sorted ascending, values rounded to
one decimal, `{}` when the owner holds nothing.

## Not done

The plan's `tests/service/test_allocation.py` is not written yet.

**No test results — none were executed.**

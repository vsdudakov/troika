# Harness tests

Two layers, and they answer different questions.

| | Question | Cost |
| --- | --- | --- |
| [`check.py`](check.py) | Is the tree structurally intact — links, anchors, file shapes, enumerations in sync? | seconds, every commit |
| [`run.py`](run.py) | Does a gate still **catch** what it claims to catch? | minutes + model spend, on prompt changes |

You cannot unit-test a prompt. You *can* test a gate. Every role file makes a falsifiable
claim — *"an import inside a function is a Major"*, *"a changed source with no mirror test is
a Blocker"* — and the [handoff contract](../agents/README.md#handoff) makes each role write a
verdict in a fixed format. Plant the defect, run the role, assert the finding. That is the
whole idea.

## Run it

```bash
python3 tests/run.py --check                 # fixtures only, no model, no spend
python3 tests/run.py --dry-run               # print the exact prompt a role receives
python3 tests/run.py --runs 5                # real runs, catch rate per case
python3 tests/run.py --case clean --runs 5   # one case
```

The agent command is configurable and must read a prompt on stdin, write the reply to stdout:

```bash
HARNESS_CMD='claude -p --model claude-fable-5 --effort high' python3 tests/run.py --runs 5
HARNESS_CMD='codex exec -m gpt-5.6-sol -'                    python3 tests/run.py --runs 5
```

**Always `--runs 5` or more.** Models are stochastic; a single run tells you nothing. Read the
rate, not the pass/fail.

## What the cases are

`fixtures/repo` is a tiny layered Python app (`api → service → repository → models`).
`fixtures/plan.md` is an approved plan for it. `cases/_base/files/` implements that plan
**correctly** — and every case is that base plus exactly one planted defect. A miss is
therefore the gate failing, never the diff being ambiguous.

| Case | Planted | Should be caught as | Check |
| --- | --- | --- | --- |
| `clean` | nothing | `Approve` / `Approve with nits` | **control** |
| `nits-only` | two comments restating the code | `Approve with nits` — Nits must **not** gate | **control** |
| `requirement-not-implemented` | requirement 3's route absent, work log claims it done | `Blocker` | 1 |
| `scope-creep` | a destructive route the plan never asked for | `Major` | 1 |
| `import-in-function` | repository import deferred into the function body | `Major` | 2 |
| `layering-violation` | `api` imports `repository`, skipping `service` | `Major` | 4 |
| `n-plus-one` | per-portfolio repository call, batched one sits unused | `Major` | 5 |
| `source-without-mirror-test` | new `allocation.py`, its mirror test deleted | `Blocker` | 6 |
| `test-asserts-nothing-real` | tests assert only `is not None` / `isinstance` | `Blocker` | 6 |
| `work-log-overstates-collection` | clean code, work log claims 14 collected against 9 written | `Blocker` | 6 |
| `contract-mismatch` | returns `list[tuple]`, plan pins `dict[str, float]` | `Major` | 8 |
| `secret-in-diff` | hardcoded live-looking API key | `Blocker` | 9 |
| `ai-attribution` | comment naming an AI product | `Blocker` | 9 |
| `debug-print` | `print("DEBUG …")` left in the hot path | `Major` | 9 |
| `truncated-file` | new file ends mid-function, no return | `Blocker` | 9 |

Eight of the [reviewer's nine checks](../agents/reviewer.md#rules) have at least one case.
Check 3 (verification commands) and check 7 (migrations) do not: the runner tells the role to
assume lint passed, and the toy repo has no schema.

**The two controls matter as much as the thirteen defects.** A gate that flags everything
passes every injection test and is worthless — `clean` catches that, and `nits-only` catches
the subtler version where a reviewer blocks the flow on style the harness says must not gate.

## Measuring a prompt change

This is what the suite is for:

```bash
git stash                                   # or check out the other revision
python3 tests/run.py --runs 5   > /tmp/before.txt
git stash pop
python3 tests/run.py --runs 5   > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt
```

If catch rate holds, the change was free. If `import-in-function` drops from 5/5 to 3/5, the
edit cost you a gate — which is a thing you can now see rather than argue about.

## Adding a case

1. `mkdir cases/<name>`, write `expect.yaml`.
2. Put **only the files that differ from `_base`** in `cases/<name>/files/`, or list paths to
   delete under `remove:`. Keeping the delta small is what makes a failure diagnosable.
3. `python3 tests/run.py --check`, then `--dry-run --case <name>` and read the diff it built.

`expect.yaml`:

```yaml
role: reviewer                  # agents/<role>.md
skill: internal-review          # skills/<skill>.md
remove: [path/to/delete.py]     # optional
verdict: [Request changes]      # acceptable verdict lines
expect_finding:                 # or `null` for a clean case
  severity: Blocker
  file: app/service/allocation.py
  keywords_any: [mirror, missing test, untested]
forbid_severity: [Blocker, Major]   # clean cases only
why: >
  Why this case is unambiguous.
```

Grading is deliberately fuzzy on wording and strict on structure: the finding must carry the
right **severity**, name the right **file**, and hit at least one keyword. Models will not
reproduce an exact sentence, and asserting on one would make the suite useless.

## Limits

- The three cases all exercise the **reviewer**. Gates owned by tester, QA, and releaser have
  no coverage yet — tester cases need `pytest` installed and a real run.
- Nothing here tests the orchestrator: lane assignment, parallelism, and the caps are
  unmeasured.
- A passing suite means these three defects are caught. It does not mean the harness is good.

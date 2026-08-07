---
title: Testing
description: You cannot unit-test a prompt, but you can test a gate. Two suites — one structural and free, one behavioural and paid.
---

# Testing

Two layers, answering different questions.

| | Question | Cost |
| --- | --- | --- |
| `tests/check.py` | Is the tree structurally intact? | seconds, every commit |
| `tests/run.py` | Does a gate still **catch** what it claims to? | minutes plus model spend |

```bash
make check         # structural
make test-check    # behavioural fixtures, no model, no spend
make test RUNS=5   # behavioural, real runs
```

CI runs the structural gate on every pull request. The model runs stay manual — they cost
money and they are stochastic.

## The structural gate

`check.py` validates the things that break silently:

- every markdown link and anchor resolves, in-tree and into the profile
- every profile anchor a role cites exists in `PROFILE.template.md`, so a *fresh* workspace does
  not inherit a dead link
- role and skill file shapes match what `ROLES.md` and `skills/README.md` declare
- every procedure declares its stop conditions, and nothing that is not a procedure does
- the profile template's anchor table and its skeleton list the same anchors — drift between
  them is either an anchor no role is told about, or a heading a fresh workspace never gets
- the behavioural fixtures' own profile answers every anchor the template declares, so a case
  never runs against a thinner profile than the roles were written for
- every behavioural case names a role and a skill that exist, and says why it exists
- the reviewer's nine checks match the copies of that list in the review skills, **in order**
- the generated commands and the manifest's command list are current
- no file hardcodes a path the workspace is allowed to move
- the version agrees across all four manifests
- the resolver resolves — run against a purpose-built temporary workspace, including the case
  where a repo's own `AGENTS.md` must *not* be mistaken for a workspace, and `--init` creates
  the `.troika/` it later resolves

## The behavioural gate

You cannot unit-test a prompt. You *can* test a gate. Every role file makes a falsifiable
claim — *"an import inside a function is a Major"*, *"a changed source with no mirror test is a
Blocker"* — and the handoff contract makes each role write its verdict in a fixed format. So:
plant the defect, run the role, assert the finding.

`fixtures/repo` is a tiny layered app (`api → service → repository → models`).
`fixtures/plan.md` is an approved plan for it. `cases/_base` implements that plan
**correctly** — and every case is that base plus exactly **one** planted defect, so a miss is
the gate failing rather than the diff being ambiguous.

Twenty-one cases cover all nine checks: a deferred import, a skipped layer, an N+1, a missing
mirror test, tests that assert only `is not None`, a test that patches the repository it
exists to exercise, a hand-edited migration, a contract mismatch, a secret, a committed
`.env`, a debug print, commented-out code, a comment that restates the line under it, a
truncated file, a work log that overstates its collected count, and more.

### The two controls matter as much as the defects

A gate that flags everything passes every injection test and is worthless. So two of the
twenty-one cases have **no defect**:

- `clean` — a correct diff must come back `Approve`.
- `nits-only` — a diff whose only problems are nits must **not** be blocked.

### Grading

Strict on structure, fuzzy on wording: the finding must carry the right severity, name the
right file, and hit at least one keyword. Models will not reproduce an exact sentence, and
asserting on one would make the suite useless.

A case may only pin a severity that the role file pins. That is measured, not assumed — see
[the nine checks](guides/review.md#severity-and-where-it-comes-from).

## Measuring a prompt change

This is what the suite is for:

```bash
python3 tests/run.py --runs 5 > /tmp/before.txt   # old revision
python3 tests/run.py --runs 5 > /tmp/after.txt    # new revision
diff /tmp/before.txt /tmp/after.txt
```

If the catch rate holds, the change was free. If `import-in-function` drops from 5/5 to 3/5,
the edit cost you a gate — which is now a thing you can see rather than argue about.

**Always `--runs 5` or more.** Models are stochastic; a single run tells you nothing.

## Any agent, either CLI

The suite drives whatever command you give it, as long as it reads a prompt on stdin and
writes the reply to stdout:

```bash
make test AGENT='claude -p --model claude-fable-5 --effort high'
make test AGENT='codex exec -m gpt-5.6-sol -'
```

## Limits, stated plainly

- Every case exercises the **reviewer**. Gates owned by tester, QA and releaser have no
  coverage yet.
- Nothing tests the orchestrator: lane assignment, parallelism and the caps are unmeasured.
- A passing suite means these twenty-one defects are caught. It does not mean the pipeline is
  good.

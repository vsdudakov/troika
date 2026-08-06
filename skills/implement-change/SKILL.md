---
name: implement-change
description: Implements one repo's part of an approved plan in its own worktree, with unit tests written but not run, ending at the profile's verification commands — no commit, no PR.
---

# Implement change (one repo)

Implement one repo's approved work and tests.

**Kind** procedure · **Used by** [backend-dev](../../agents/backend-dev.md) · [frontend-dev](../../agents/frontend-dev.md) · **When** the plan passes review (develop-flow step 3) · **Ends with** code written, tests written and **collected but never executed**, and every verification command the profile lists for the touched areas green — **not** a commit or PR; [release-pr.md](../release-pr/SKILL.md) does that after review, tests, and QA

Set `WS`; scratchpad paths are absolute.

## 1. Read the plan

Read `$TROIKA_SCRATCHPAD/plans/<TICKET>.md`. Take only your repo. Missing or contradictory work stops; never re-plan.

Read the workspace's memory too — `ls $TROIKA_MEMORY/*.md`, there is no index file ([memory](../memory/SKILL.md)). These entries are written by dev and test roles about exactly this work: a repo mid-migration, a suite that only fails in parallel, a green result that did not mean what it looked like.

## 2. Branch in a worktree — one per repo, not one per role

Check for the repo lane first:

```bash
git worktree list | grep "<repo>-<TICKET>"
```

- **Exists:** join it, read prior work log, stay in owned paths. Never create a second repo lane.
- **Missing:** create from profile `<BASE>` with the contractual name:

```bash
git fetch <remote>
git worktree add "$TROIKA_WORKTREES/<repo>-<TICKET>" -b <branch, per the profile> <BASE>
```

Use profile dependency symlinks; do not reinstall. Apply profile signing config, once per worktree. Index the worktree as its own root.

<a id="claim"></a>
**Claim the lane before writing anything.** The work log only exists once you finish, so it cannot mark a lane that is *in progress* — the claim file is what makes "one role writes a worktree at a time" checkable instead of merely stated ([worktree › Lane claim](../worktree/SKILL.md#claim)):

```bash
LANE="$TROIKA_SCRATCHPAD/lanes/<repo>-<TICKET>"
cat "$LANE" 2>/dev/null && echo "held — stop and report"   # another role has it
mkdir -p "$TROIKA_SCRATCHPAD/lanes" && echo "<role> $(date -u +%FT%TZ)" > "$LANE"
```

Release it as the last thing you do, after the work log is written: `rm -f "$LANE"`. A stale claim from a crashed role is reported, never deleted silently — it means a worktree may hold half-finished work.

## 3. Implement

Follow profile [rules](../../../AGENTS.md#rules), [style](../../../AGENTS.md#style), [layering](../../../AGENTS.md#layering), and role.

Imports stay at top. Fix cycles by direction, lower layer, or split; never defer imports. Stop if scope cannot support the fix.

Migrations: generate with the repo's command ([AGENTS.md › Commands](../../../AGENTS.md#commands)) — never hand-edit an applied migration.

<a id="tests"></a>
## 4. Tests, with the code — written, not run

Write tests; execute none. [Tester](../../agents/tester.md) runs change tests (step 5); CI runs all (step 8). You get no red-green loop, so they must be right on the first pass — but you do get [collection](#collect), which is not a run.

- Mirror every changed or created source file, at the path the profile fixes.
- Cover every guard, exception, early return, and error state.
- Follow profile framework/location/mocking rules.
- Assert behavior, not calls.
- Record exact node IDs mapped to sources.

Re-read fixtures, imports, discovery, assertions — then collect them ([below](#collect)).

<a id="verify"></a>
## 5. Verify — gate

Run exactly the profile's verification commands for touched areas — none invented, none skipped. Final code must pass.

**No test executes here** — not a targeted run, not a single node ID "just to check".

<a id="collect"></a>
**Collect them, though.** Run the framework's collection-only mode over the test files you wrote — `pytest --collect-only <paths>` or the profile's equivalent ([AGENTS.md › Commands](../../../AGENTS.md#commands)). It runs no assertion and no fixture body, so the no-red-green-loop design holds and the tester still owns the first real execution. What it does catch is exactly what a blind writer produces: an unresolved import, a missing fixture, a parametrize list that collects nothing, a name outside the discovery pattern. Each of those costs a full step 4 + step 5 cycle if it reaches the tester instead. Confirm the collected count equals the number of tests you wrote, and put both in the work log.

**Never run a formatter or auto-fixing lint target in a worktree whose dependency directory is a symlink** — it walks the shared environment and rewrites it. Remove the symlink first, format from the primary clone, or use the profile's read-only variant ([AGENTS.md › Gotchas](../../../AGENTS.md#gotchas)).

<a id="notests"></a>
### No-test exception

If a fixture or snapshot cannot be written without executing something — a shape you cannot infer, a snapshot that must be generated — record it and its node ID for the tester. Collection is still allowed; a local run is not.

Pre-existing failures on the base branch are not yours to fix — name them in the report.

## 6. Self-check before reporting

- Every requirement for this repo implemented; nothing extra.
- Every changed source and branch maps to a test, and collection reports that exact number.
- Every verification command the profile lists for your areas is green.
- New files complete (`wc -l`, import check) — truncated files have shipped before.
- No import inside a function, method, or component in the diff.
- No secrets, no `.env`, no debug prints, no AI attribution anywhere.

## Output

Write `$TROIKA_SCRATCHPAD/plans/<TICKET>-<role>.md` by absolute path.

Contents, and the same back to the orchestrator: branch · worktree path (and whether you created or joined it) · files changed · **the exact node IDs of every test you wrote or changed**, and which source file each mirrors · the verification commands you ran and their results (decisive line on failure) · the contract as actually implemented · anything you could not test without running something · anything from the plan not done and why.

Include the **collection command and the count it reported**; review gates on that number matching the node IDs above.

**No test results** — you executed none. A work log claiming a green test run in this phase is wrong by construction; a collected count is not a run.

## Stop conditions

Write a [`memory/`](../memory/SKILL.md) entry when something failed for a reason the docs did not predict, or a green result turned out not to mean what it looked like — with the cost.

Stop and report instead of improvising when: the plan is missing something you need or contradicts the code; the work would touch another role's paths or a repo the workspace marks out of scope; the branch needs a dependency change you cannot make without breaking the shared environment; or a verification command fails for a reason that predates your diff.

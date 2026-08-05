---
name: run-unit-tests
description: Runs only the unit tests the change developed — plus the existing ones directly tied to the changed sources — one parallel lane per area, and routes every failure back to the owning dev role.
---

# Run unit tests (changed only, parallel)

The first execution of the change's tests. Dev roles wrote them and did **not** run them ([implement-change › Tests](implement-change.md#tests)); this pass runs them, narrowed to the change and spread across parallel lanes.

**Kind** procedure · **Used by** [tester](../agents/tester.md) · **When** internal review is `Approve` / `Approve with nits`, before QA (develop-flow step 5) · **Ends with** a test report file, a `Pass`/`Fail` verdict, and failures routed to the owning dev role

Never edits product code and never edits a test. Reports the failure; the owning dev role fixes it. Set `WS` first ([AGENTS.md › Workspace paths](../../AGENTS.md#workspace-paths)).

<a id="selection"></a>
## 1. Select the tests — from the diff, not from the tree

Per worktree, from the dev role's work log. Untracked files must be staged as intent-to-add first or new tests are invisible to `diff` ([internal-review › Diff](internal-review.md#diff-new-files)):

```bash
cd "$WS/llm/worktrees/<worktree>"
git add -N -- .
git --no-pager diff --name-only origin/main...HEAD
git --no-pager diff --name-only
```

From that file list, three tiers — and nothing else:

1. **Test files in the diff** — every test file added or modified. Always run, no exception.
2. **The mirror test of every changed source file** — the profile fixes where a source file's test lives ([AGENTS.md › Tests](../../AGENTS.md#tests)); resolve each changed source to that path and run it if it exists. A changed source whose mirror test does **not** exist is a review defect, not a test-selection problem: report it and hand it back.
3. **Tests directly tied to a changed symbol** — an existing test that imports the changed module, or exercises a function, class, endpoint, or migration the diff changed. Resolve this by symbol search over the test tree ([AGENTS.md › Code search](../../AGENTS.md#code-search)), not by guessing.

**Directly tied means the test names the thing.** A test that imports the changed module qualifies. A test two layers away that *might* be affected does not — that is a regression, and regressions are CI's job on the whole suite (develop-flow step 8). Do not widen the selection to a package, an app, or a directory because it "feels related": a run that widens to the suite defeats the point of this step and costs the fix cycle tens of minutes.

Write the selected node IDs down before running. That list goes in the report and is what makes the run reproducible.

<a id="lanes"></a>
## 2. Run — one lane per area, all lanes at once

Group the selected tests by **area** — the unit the profile gives a distinct test command to ([AGENTS.md › Commands](../../AGENTS.md#commands)): one backend package, one client app, one extension, one compiled service. Each area is one lane.

**Lanes run concurrently, not in sequence, and across every worktree that is ready.** A repo still in development or still in review contributes no lanes and holds none up — run what is ready, run the rest when it arrives. Wall clock is the slowest lane, not the sum. Each lane runs in its own worktree directory with that area's test command from the profile, narrowed to that lane's node IDs, with the profile's coverage flags left at their full value.

Inside a lane, use the runner's own parallel flag where the profile documents one ([AGENTS.md › Commands](../../AGENTS.md#commands)) — except where the profile marks a suite sequential, which is a correctness constraint and not a speed trade ([AGENTS.md › Gotchas](../../AGENTS.md#gotchas)).

Two ways to get lanes concurrent, both acceptable: one subagent per lane, or background shells per lane joined at the end. Whichever runs, capture each lane's full output to `$WS/llm/scratchpad/plans/<TICKET>-tests-<n>-<area>.log` — a lane that fails is read from its log, not re-run to see what happened.

Never run the area's `test`-style target unnarrowed: those targets walk the whole tree.

<a id="reading"></a>
## 3. Read the result — a zero exit code is not a pass

Per lane, confirm all four before calling it green:

- The run collected the tests you selected — a typo in a node ID collects zero tests and still exits 0 on some runners.
- The count run matches the count selected.
- The coverage summary was reached, where the profile's command produces one, and the missing-lines list is empty for the changed files.
- No wrapper swallowed a crash ([AGENTS.md › Gotchas](../../AGENTS.md#gotchas)).

Quote the shortest decisive line for each failure — the assertion or error line, not the whole traceback.

## 4. Route failures

A failure belongs to the dev role that owns the repo, never to this one:

- **Test fails because the test is stale or wrong** — the production contract moved and the test still asserts the old shape → the **test** is what changes, never the production code loosened to make it pass.
- **Test fails because the code is wrong** → the code changes, with the test left asserting the real requirement.
- **Fails on clean `main` too** — verify in the primary clone before claiming it, then name it as pre-existing and do not fix it here.

After the dev role fixes, re-run **the same selection** plus any test the fix added or changed, and re-run [internal-review.md](internal-review.md) on the new diff before advancing — a fix is a diff, and no diff reaches QA unreviewed.

**Cap: 3 cycles.** Third run still failing → stop the flow and report the failing node IDs and their decisive lines to the human.

## Output

Write the report to `$WS/llm/scratchpad/plans/<TICKET>-tests-<n>.md` (`<n>` = cycle, from 1) **and** return it to the orchestrator. [releaser](../agents/releaser.md) reads the highest-numbered one at its gate ([handoff contract](../agents/README.md#handoff)).

```markdown
- Selection: <count> tests · <count> changed test files · <count> mirror tests · <count> symbol-tied tests
- Lanes: <area> (<count>) · <area> (<count>) — run concurrently
- Result per lane: <area> <Pass | Fail> — <counts> · coverage <line, or N/A>
- Not selected on purpose: <what was in the diff's blast radius but left to CI>

### Failures
- `<node id>` — <decisive line> · owner <role> · <test wrong | code wrong | pre-existing on main>

### Verdict
<Pass | Fail> — <one sentence>
```

Node IDs are exact and copy-pasteable: the human re-runs them.

## Stop conditions

Stop and report instead of widening the run when: a changed source file has no mirror test (review missed it); a lane's command is not in the profile for that area; a worktree named in a work log is missing ([worktree › Gotchas](worktree.md#gotchas)); the selection cannot be resolved without reading the whole tree; or the third cycle is still red.

Write a [`memory/`](../memory/README.md) entry when a green run turned out not to mean what it looked like — a swallowed crash, a zero-collection pass, a suite that only fails in parallel.

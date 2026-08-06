---
name: run-unit-tests
description: Runs only the unit tests the change developed — plus the existing ones directly tied to the changed sources — one parallel lane per area, and routes every failure back to the owning dev role.
---

# Run unit tests (changed only, parallel)

First test execution: change-related tests only, parallel by area.

**Kind** procedure · **Used by** [tester](../../agents/tester.md) · **When** internal review is `Approve` / `Approve with nits`, before QA (develop-flow step 5) · **Ends with** a test report file, a `Pass`/`Fail` verdict, and failures routed to the owning dev role

Read-only. Owner fixes failures. Set `TROIKA_WORKSPACE`.

<a id="selection"></a>
## 1. Select the tests — from the diff, not from the tree

Read `ls $TROIKA_MEMORY/*.md` first — there is no index file ([memory](../memory/SKILL.md)). Entries about swallowed crashes, zero-collection passes, and suites that only fail in parallel are written by this role, for this role.

Per worktree, use profile `<BASE>`. Intent-to-add exposes untracked files:

```bash
BASE=<remote>/<default-branch>        # PROFILE.md › Branches
cd "$TROIKA_WORKTREES/<worktree>"
git fetch "${BASE%%/*}"
git add -N -- .
git --no-pager diff --name-only "$BASE"...HEAD
git --no-pager diff --name-only
```

Run only:

1. **Test files in the diff** — every test file added or modified. Always run.
2. **The mirror test of every changed source file** — the profile fixes where a source file's test lives (PROFILE.md › Tests (`#tests`)); resolve each changed source to that path and run it if it exists. A changed source with no mirror test is a review defect, not a selection problem: report it and hand it back.
3. **Tests directly tied to a changed symbol** — an existing test that imports the changed module or exercises a function, class, endpoint, or migration the diff changed. Resolve by symbol search over the test tree (PROFILE.md › Code search (`#code-search`)), not by guessing.

Direct means the test names/imports the symbol. CI owns indirect regression. Record node IDs before running.

<a id="lanes"></a>
## 2. Run — one lane per area, all lanes at once

One lane per profile command area. Run ready lanes concurrently in their worktrees, narrowed to node IDs, full coverage flags.

Inside a lane, use the runner's parallel flag where the profile documents one — except where the profile marks a suite sequential, which is correctness, not a speed trade (PROFILE.md › Gotchas (`#gotchas`)).

Use parallel workers or joined background shells. Log each lane to `$TROIKA_SCRATCHPAD/plans/<TICKET>-tests-<n>-<area>.log` — a failing lane is read from its log, never re-run to see what happened.

Never run an area's `test`-style target unnarrowed: those walk the whole tree.

<a id="reading"></a>
## 3. Read the result — a zero exit code is not a pass

Per lane, confirm all four before calling it green:

- The run collected the tests you selected — a typo in a node ID collects zero and still exits 0 on some runners.
- The count run matches the count selected.
- The coverage summary was reached where the profile's command produces one, and the missing-lines list is empty for the changed files.
- No wrapper swallowed a crash (PROFILE.md › Gotchas (`#gotchas`)).

Quote the shortest decisive line per failure — the assertion or error line, not the whole traceback.

## 4. Route failures

Route to code owner:

- **Test stale or wrong** — the production contract moved and the test asserts the old shape → the **test** changes; production code is never loosened to pass.
- **Code wrong** → the code changes, with the test left asserting the real requirement.
- **Fails on the base branch too** — verify in the primary clone before claiming it, then name it as pre-existing and do not fix it here.

After fix, re-review; rerun same selection plus new/changed tests. Cap at 3 cycles.

## Output

Write to `$TROIKA_SCRATCHPAD/plans/<TICKET>-tests-<n>.md` (`<n>` = cycle, from 1) **and** return it to the orchestrator. [releaser](../../agents/releaser.md) reads the highest-numbered one ([handoff contract](../../ROLES.md#handoff)).

```markdown
- Selection: <count> tests · <count> changed test files · <count> mirror tests · <count> symbol-tied tests
- Lanes: <area> (<count>) · <area> (<count>) — run concurrently
- Result per lane: <area> <Pass | Fail> — <counts> · coverage <line, or N/A>
- Not selected on purpose: <what was in the diff's blast radius but left to CI>

### Failures
- `<node id>` — <decisive line> · owner <role> · <test wrong | code wrong | pre-existing on base>

### Verdict
<Pass | Fail> — <one sentence>
```

Node IDs must be copy-pasteable.

## Stop conditions

Stop and report instead of widening the run when: a changed source file has no mirror test (review missed it); a lane's command is not in the profile for that area; a worktree named in a work log is missing ([worktree › Gotchas](../worktree/SKILL.md#gotchas)); the selection cannot be resolved without reading the whole tree; or the third cycle is still red.

Write a [`memory/`](../memory/SKILL.md) entry when a green run turned out not to mean what it looked like — a swallowed crash, a zero-collection pass, a suite that only fails in parallel.

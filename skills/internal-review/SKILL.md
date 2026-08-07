---
name: internal-review
description: Reviews the local branch diff before QA and before any push — catches layering, coverage, style, and hygiene defects that QA cannot see. Posts nothing outside the workspace.
---

# Internal review (pre-PR)

Pre-push local diff review.

**Kind** procedure · **Used by** [reviewer](../../agents/reviewer.md) · **When** dev roles report done and before any push — alongside the tester, not before it ([develop-flow › 4 ∥ 5](../develop-flow/SKILL.md#review-tests)) · **Ends with** a verdict file and a loop back to the dev role, nothing posted outside the workspace

Read-only: no edit, push, or test. Set `TROIKA_WORKSPACE`.

## 1. Requirements

Read plan and dev work log; they define scope.

<a id="diff-new-files"></a>
## 2. Diff

From the dev role's worktree. `<BASE>` is the profile's base ref, resolved once ([worktree › The base ref](../worktree/SKILL.md#base-ref)) — never hardcoded:

```bash
BASE=<remote>/<default-branch>                   # PROFILE.md › Branches
git fetch "${BASE%%/*}"
git status --short                               # untracked files show as ??
git add -N -- .                                  # intent-to-add, so new files enter the diff
git --no-pager diff "$BASE"...HEAD               # committed work
git --no-pager diff                              # uncommitted, now including new files
git --no-pager diff --stat "$BASE"...HEAD
```

Account for every `??` — an untracked, unreviewed file ships unseen. `git add -N` records intent-to-add so new files enter the diff; their content stays unstaged and release commits normally afterwards. Review the whole diff and needed context.

<a id="cycle-scope"></a>
### Cycle 2 and after — the fix's files, not the diff again

A re-review reads what the fix changed, resolved from the previous cycle's snapshot ([develop-flow › Re-entry](../develop-flow/SKILL.md#reentry)), never from the dev role's account of what it touched:

```bash
{ git --no-pager diff --name-only "$BASE"...HEAD; git --no-pager diff --name-only; } \
  | sort -u | xargs -r shasum > "$TROIKA_SCRATCHPAD/plans/<TICKET>-<repo>-cycle-<n>.sha"
diff "$TROIKA_SCRATCHPAD/plans/<TICKET>-<repo>-cycle-<n-1>.sha" \
     "$TROIKA_SCRATCHPAD/plans/<TICKET>-<repo>-cycle-<n>.sha"     # the fix's files
```

Run all nine checks over those files, and re-check every finding `-review-<n-1>.md` raised — a narrowed diff never means a narrowed verdict, and a Blocker is not closed because the file it lived in stopped being read. Widen back to the whole diff under [the widening rules](../develop-flow/SKILL.md#widen): a shared model, base class, utility, config, middleware, public contract, migration, or inherited fixture among the fix's files; a missing previous snapshot; or the last cycle the loop cap allows.

Write the snapshot at the end of **every** cycle, including the first, whatever the verdict. The next cycle has nothing to diff against otherwise, and a cycle with nothing to diff against runs at full scope.

<a id="runner"></a>
### Running this pass on the other family

Preferred for independent review. **The tool and the exact command are the workspace's** — PROFILE.md › Review runner (`#review-runner`), diff pass — and it must cover staged, unstaged **and** untracked files, which is what step 2's `git add -N` prepares:

```bash
cd "$TROIKA_WORKTREES/<repo>-<TICKET>"
cat "$TROIKA_PROFILE" \
    "${CLAUDE_PLUGIN_ROOT}/agents/reviewer.md" \
    "${CLAUDE_PLUGIN_ROOT}/skills/internal-review/SKILL.md" \
    "$TROIKA_SCRATCHPAD/plans/<TICKET>.md" \
    "$TROIKA_SCRATCHPAD/plans/<TICKET>-<role>.md" \
  | <the profile's diff-pass review command>
```

For work already committed on the branch, use the profile's base-ref form of that command. Model and effort come from the `reviewer` row of PROFILE.md › Models and effort (`#models`); where the profile declares no separate runner, run the pass in a fresh session on that row. Follow [output](#output).

## 3. Checks

The nine checks and their definitions are in [reviewer › Rules](../../agents/reviewer.md#rules): requirements, code style, verification, layering, queries, tests present, migrations, contract match, hygiene.

Internal-pass specifics:

- **Verification:** run only profile commands; quote decisive failure.
- **Tests:** mirror every source/branch; real behavior; node IDs match diff. Missing/hollow is Blocker.
- **Runnable:** the work log must carry a collected count matching the tests written ([collect](../implement-change/SKILL.md#collect)); a missing or short count is a Blocker, because nothing else has proved these files even import. Read for what collection cannot see: a fixture that resolves but returns the wrong shape, an assertion that passes for the wrong reason.
- **Regression:** name shared model/base/util/config/middleware/migration/public-contract blast radius left to CI.
- **Bug tickets:** the diff must carry a regression test that encodes what `$TROIKA_SCRATCHPAD/plans/<TICKET>-repro-<n>.md` recorded — same input, same path, asserting the corrected behaviour. Read it against the reproduction, not against the brief's prose: a test that would pass on the base ref has not encoded the bug, and that is a Blocker under check 6.

## 4. Report

Use the [reviewer output format](../../agents/reviewer.md#output).

## 5. Loop

Blocker/Major → owner fixes/verifies; re-review at [cycle scope](#cycle-scope). Fix cheap nits.

Each cycle after the first runs **one effort tier below the reviewer's row** ([develop-flow](../develop-flow/SKILL.md)) — except a widened cycle and the last one the cap allows, which keep the row's effort. Name the tier in the report.

## Output

Say at the top of every report which scope the cycle ran at — whole diff, the fix's files, or widened by a named file — and at which effort tier. A cycle whose scope nobody can name cannot be trusted to have covered anything.

Write the report to `$TROIKA_SCRATCHPAD/plans/<TICKET>-review-<n>.md` (`<n>` = cycle, from 1) **and** return it to the orchestrator. That file is the release gate's evidence — [releaser](../../agents/releaser.md) runs in a separate context and reads the highest-numbered one ([handoff contract](../../ROLES.md#handoff)).

Nothing leaves the workspace, so this report skips [commenter](../../agents/commenter.md) — internal, terse, for the dev role to act on.

## Stop conditions

**Cap at the profile's loop cap (`#loops`, default 3) cycles.** The last allowed review still holding Blockers or Majors → stop the flow and report the unresolved findings. Also stop if the diff no longer matches the plan's scope, or a worktree named in the work log is missing ([worktree › Gotchas](../worktree/SKILL.md#gotchas)).

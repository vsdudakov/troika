---
name: internal-review
description: Reviews the local branch diff before QA and before any push — catches layering, coverage, style, and hygiene defects that QA cannot see. Posts nothing outside the workspace.
---

# Internal review (pre-PR)

The pre-push pass on the local branch diff. Catches what QA can't see (layering, coverage, style) and what CI would otherwise catch late.

**Kind** procedure · **Used by** [reviewer](../agents/reviewer.md) · **When** dev roles report done, before the tests run and before any push (develop-flow step 4) · **Ends with** a verdict file and a loop back to the dev role, nothing posted outside the workspace

Read-only: never edit code, never push, and **never run a test** — no test has run yet and running one is step 5's job ([tester](../agents/tester.md)). Set `WS` first ([AGENTS.md › Workspace paths](../../AGENTS.md#workspace-paths)).

## 1. Requirements

Read `$WS/llm/scratchpad/plans/<TICKET>.md` and the dev role's work log `$WS/llm/scratchpad/plans/<TICKET>-<role>.md`. Those are the requirements the diff must meet.

<a id="diff-new-files"></a>
## 2. Diff

From the dev role's worktree. `<BASE>` is the profile's base ref, resolved once ([worktree › The base ref](worktree.md#base-ref)) — never hardcoded:

```bash
BASE=<remote>/<default-branch>                   # AGENTS.md › Branches
git fetch "${BASE%%/*}"
git status --short                               # untracked files show as ??
git add -N -- .                                  # intent-to-add, so new files enter the diff
git --no-pager diff "$BASE"...HEAD               # committed work
git --no-pager diff                              # uncommitted, now including new files
git --no-pager diff --stat "$BASE"...HEAD
```

**New files are the trap.** Development stays uncommitted until release, so a new source file, test, or migration appears in neither `diff` until `git add -N` stages its existence. Run `git status --short` first and account for every `??` entry — an untracked, unreviewed file ships unseen. `git add -N` changes no content, and release commits normally afterwards.

Review the whole diff, not a sample. Read the surrounding file when a hunk's correctness depends on it.

<a id="runner"></a>
### Running this pass in Codex

Preferred when another tool wrote the code: an independent model reading the diff catches what the writing model cannot see. `codex exec review --uncommitted` covers staged, unstaged **and untracked** changes, so it needs no `git add -N` workaround.

```bash
cd "$WS/llm/worktrees/<repo>-<TICKET>"
cat "$WS/AGENTS.md" \
    "$WS/llm/agents/reviewer.md" \
    "$WS/llm/skills/internal-review.md" \
    "$WS/llm/scratchpad/plans/<TICKET>.md" \
    "$WS/llm/scratchpad/plans/<TICKET>-<role>.md" \
  | codex exec review --uncommitted -
```

Profile, role, and skill files are piped in as the prompt because they live outside the repo Codex has open. Use `--base <default-branch>` instead of `--uncommitted` if the work is already committed. Model and effort come from [reviewer](../agents/reviewer.md) (`gpt-5.6-sol`, high) — override with `-m` / `-c model_reasoning_effort="high"`.

Whatever runs it, the output must be the [reviewer format](../agents/reviewer.md#output) and land in the file named under [Output](#output) — the release gate reads that file, not a terminal transcript.

## 3. Checks

The nine checks and their definitions are in [reviewer › Rules](../agents/reviewer.md#rules): requirements, code style, lint, layering, queries, tests present, migrations, contract match, hygiene.

Four are done differently here than in the PR pass:

- **Lint and type check** — run exactly the verification commands the profile lists for the touched areas ([AGENTS.md › Commands](../../AGENTS.md#commands)) in the worktree; no command the profile does not list. Quote the shortest decisive failing line.
- **Tests present** — the heaviest check here, because **nothing has run these tests yet**. Verify from the diff that every changed source file has its mirror test ([AGENTS.md › Tests](../../AGENTS.md#tests)), that each asserts real behaviour rather than a mock having been called, and that every branch in the diff — each guard, `except`, early return — has a test reaching it. Missing or hollow is a **Blocker**: it costs a cycle in step 5 and a red PR on CI. Cross-check the work log's node IDs against the test files actually in the diff; a claimed test that is not there is the failure mode this catches.
- **Tests that will not run** — read them as a runner would: an import that does not resolve, a missing fixture, a parametrize list that collects nothing, a name outside the runner's discovery pattern. These were written blind, so mechanical defects are likely and cost a whole cycle in step 5.
- **Regression risk nobody sees before CI** — step 5 runs only the change's own tests, so call out a diff touching a shared model, base class, util, config, middleware, migration, or an existing public signature. Name the blast radius: it is what CI is being trusted to cover.

## 4. Report

Use the [reviewer output format](../agents/reviewer.md#output).

## 5. Loop

Blockers and Majors go back to the owning dev role; it fixes, re-runs the profile's verification commands, and this skill runs again on the new diff. Nits fixed when cheap. Repeat until `Approve` / `Approve with nits`.

## Output

Write the report to `$WS/llm/scratchpad/plans/<TICKET>-review-<n>.md` (`<n>` = cycle, from 1) **and** return it to the orchestrator. That file is the release gate's evidence — [releaser](../agents/releaser.md) runs in a separate context and reads the highest-numbered one ([handoff contract](../agents/README.md#handoff)).

Nothing leaves the workspace, so this report skips [commenter](../agents/commenter.md) — internal, terse, for the dev role to act on.

## Stop conditions

**Cap at 3 cycles.** Third review still holding Blockers or Majors → stop the flow and report the unresolved findings. Also stop if the diff no longer matches the plan's scope, or a worktree named in the work log is missing ([worktree › Gotchas](worktree.md#gotchas)).

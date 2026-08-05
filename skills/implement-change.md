---
name: implement-change
description: Implements one repo's part of an approved plan in its own worktree, with unit tests, ending at green tests and lint — no commit, no PR.
---

# Implement change (one repo)

One repo's share of an approved plan, in its own worktree, with the tests that prove it.

**Kind** procedure · **Used by** [backend-dev](../agents/backend-dev.md) · [frontend-dev](../agents/frontend-dev.md) · **When** the plan is approved (develop-flow step 3) · **Ends with** your own tests green at the profile's coverage gate and lint green — **not** a commit or PR; [release-pr.md](release-pr.md) does that after review and QA

Set `WS` first — every scratchpad path below is absolute ([AGENTS.md › Workspace paths](../../AGENTS.md#workspace-paths)).

## 1. Read the plan

`$WS/llm/scratchpad/plans/<TICKET>.md` — take only the requirements and work items for your repo. If something needed is missing or contradicts the code, stop and report; never re-plan silently.

## 2. Branch in a worktree

From inside the target repo. The worktree directory is `<repo>-<TICKET>` — QA's stack overrides and release's cleanup both assume that exact shape ([worktree](worktree.md#naming)); branch naming is in [AGENTS.md › Branches](../../AGENTS.md#branches):

```bash
git fetch origin
git worktree add "$WS/llm/worktrees/<repo>-<TICKET>" -b <dev>/<TICKET>-<fix-description> origin/main
```

Wire up dependencies with the symlinks in [AGENTS.md › Branches](../../AGENTS.md#branches) — **do not reinstall**. Use the absolute form (`"$WS/<repo>/…"`); the relative one is three or four `../` deep from `llm/worktrees/<dir>` and is easy to get wrong ([worktree › setup](worktree.md#setup)).

Set signing once per worktree: `git config commit.gpgsign true`.

Index the worktree — it is its own root, and everything you search from here reads that index ([AGENTS.md › Code search](../../AGENTS.md#code-search)).

## 3. Implement

Follow the project profile — [Rules](../../AGENTS.md#rules) · [Style](../../AGENTS.md#style) · [Layering](../../AGENTS.md#layering) — and your role file. No layer skipped. New code goes where that kind of code already lives. Comments only for a non-obvious why.

**Imports go at the top of the file, every file.** If a top-level import raises a circular-import error, do not move it into the function — the cycle is the bug. Fix the direction, move the shared piece into a lower layer, or split the module. If none of those work without changing the plan's scope, stop and report rather than deferring the import.

Migrations: generate with the repo's command ([AGENTS.md › Commands](../../AGENTS.md#commands)) — never hand-edit an applied migration.

## 4. Tests, with the code

Running fewer tests locally raises the bar on *writing* them: CI runs the full coverage gate over the whole package, so any line of yours left uncovered fails the PR, not your laptop. Write for full coverage of everything you touched, first time.

Framework, naming, location, the coverage gate, and what may be mocked are in [AGENTS.md › Tests](../../AGENTS.md#tests) — that is the whole spec, and it is a gate. The one thing this skill adds is *when to stop*: read the missing-lines output of your targeted run (step 5) and close every line it lists before reporting done. That report is the same one CI will produce, narrowed to your files.

<a id="verify"></a>
## 5. Verify — gate

**Run your own tests, not the whole suite.** The full suite runs on CI when the PR opens — that is what catches regressions outside your diff. Locally you prove one thing: the code you wrote works and is covered. A full local suite costs tens of minutes per fix cycle and buys a signal CI is about to give for free.

**Lint is not a suite** — always run the repo's full lint, and the build where the type check lives inside it. It is fast and it is the type gate.

<a id="targeted"></a>
### Targeted tests

The exact command per repo is in [AGENTS.md › Commands](../../AGENTS.md#commands). The shape is always the same: the repo's normal test runner, narrowed to the sources you changed and the tests you wrote, with the coverage gate left at its full value. Coverage stays at the profile's number — scoped to what you changed, so the gate still means something.

A repo's `make test`-style target usually runs the whole tree; a targeted run calls the test runner directly with the same flags, narrowed.

<a id="fullsuite"></a>
### When to run the full suite anyway

Targeted tests cannot see a regression you caused somewhere else. Run the repo's full suite **before reporting done** when your diff touches shared ground:

- a model, schema, base class, mixin, or shared util that other modules import
- config, settings, dependency injection, middleware, or a migration
- a signature, return type, or exception contract of an existing public function
- anything you removed or renamed

Otherwise skip it and say so in the report: **which tests you ran, and that the full suite is CI's gate**. A CI failure on the PR comes back to you ([release-pr](release-pr.md)); it is not the reviewer's or QA's to fix.

**A zero exit code is not always a pass.** Check [AGENTS.md › Gotchas](../../AGENTS.md#gotchas) — a repo may wrap its test target in a way that swallows a crash and never evaluates the coverage gate. Confirm the run reached the coverage summary before calling it green.

**Never run the repo's formatter target in a worktree whose dependency directory is a symlink** — it walks the shared environment and rewrites it. Remove the symlink first, or format from the primary clone.

Pre-existing failures on `main` are not yours to fix — name them in the report instead of hiding them.

## 6. Self-check before reporting

- Every requirement for this repo implemented; nothing extra.
- Every changed source file has a test, and the targeted run's missing-lines list is empty for your files — CI gates over the whole package and it is not negotiable there.
- Full suite run, or a deliberate skip you can justify against the shared-ground list above.
- New files complete (`wc -l`, import check) — truncated files have shipped before.
- No import inside a function, method, or component in the diff — scan the added lines for your language's import form; if one is there, the fix is the cycle, not the placement.
- No secrets, no `.env`, no debug prints, no AI attribution anywhere.

## Output

Write the work log to `$WS/llm/scratchpad/plans/<TICKET>-<role>.md` — absolute path; your cwd is inside the worktree, and a relative `llm/scratchpad/` would create one inside the product repo. `<role>` is your role's `name` (`backend-dev`, `frontend-dev`).

Contents, and the same back to the orchestrator: branch · worktree path · files changed · **exactly which tests you ran** and their result, with the coverage line for your files (decisive line on failure) · whether you ran the full suite and why or why not · lint result · the contract as actually implemented · anything from the plan not done and why.

## Stop conditions

Write a [`memory/`](../memory/README.md) entry when something failed for a reason the docs did not predict, or a green result turned out not to mean what it looked like — with the cost, which is why the next run reads it.

Stop and report instead of improvising when: the plan is missing something you need or contradicts the code; the work would touch another role's repo or one the workspace marks out of scope; the branch needs a dependency change you cannot make without breaking the shared environment; or tests fail for a reason that predates your diff.

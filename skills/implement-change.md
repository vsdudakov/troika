---
name: implement-change
description: Implements one repo's part of an approved plan in its own worktree, with unit tests written but not run, ending at green lint — no commit, no PR.
---

# Implement change (one repo)

One repo's share of an approved plan, in its own worktree, with the tests that prove it.

**Kind** procedure · **Used by** [backend-dev](../agents/backend-dev.md) · [frontend-dev](../agents/frontend-dev.md) · **When** the plan passes review (develop-flow step 3) · **Ends with** the code written, its tests written **and not run**, and the repo's full lint and type check green — **not** a commit or PR; [release-pr.md](release-pr.md) does that after review, tests, and QA

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

<a id="tests"></a>
## 4. Tests, with the code — written, not run

**You write the tests. You do not run them.** [tester](../agents/tester.md) runs them once, for every repo at the same time, in develop-flow step 5 ([run-unit-tests](run-unit-tests.md)); the full suite runs on CI when the PR opens. Two runs, both later, neither yours.

That is a real constraint: **you get no red-green loop**, so the tests have to be right on the first pass. Write them the way you would review them.

- **Every changed or created source file ships its mirror test**, at the path the profile fixes ([AGENTS.md › Tests](../../AGENTS.md#tests)). A changed file with no test is what stops the pipeline two steps later.
- **Cover every branch you touched** — each guard, each `except`, each early return, each error state. There is no coverage report in front of you; walk the diff line by line instead and name the test that covers each one.
- Framework, naming, location, and what may be mocked are in [AGENTS.md › Tests](../../AGENTS.md#tests) — the whole spec, and a gate.
- **Assert real behaviour**, not that the code was called. A test written blind that asserts a mock is a test that passes for the wrong reason and proves nothing when the tester runs it.
- **Node IDs go in your work log** — the exact paths and test names you wrote. The tester's selection starts from the diff, and your list is what it checks itself against.

Read your tests once more before reporting: a typo in a fixture or an import is a whole fix cycle in step 5.

<a id="verify"></a>
## 5. Verify — gate

**Lint, type check, build. Not tests.**

The repo's **full lint** and the build where the type check lives inside it ([AGENTS.md › Commands](../../AGENTS.md#commands)) — both green on the final code, both fast, and together they are the only automated signal you get. A syntax error, a bad import, a type mismatch, or an unused symbol in a test file surfaces here, and here is the cheapest place for it.

**Never run the repo's formatter target in a worktree whose dependency directory is a symlink** — it walks the shared environment and rewrites it. Remove the symlink first, or format from the primary clone ([AGENTS.md › Gotchas](../../AGENTS.md#gotchas)).

<a id="notests"></a>
### Why not run them here

A dev role running its own tests re-runs them on every fix cycle, in series with the other dev role, in a session that is already long. Step 5 runs the change's tests **once, across every repo's lane at the same time**, with a selection computed from the diff rather than from memory — and it does it after review has already removed the defects a test run would have found the slow way.

If a test cannot be written without running something — a fixture whose shape you cannot infer, a snapshot that must be generated — say so in the work log and hand the node ID to the tester. Do not turn that into a full local suite run.

Pre-existing failures on `main` are not yours to fix — name them in the report instead of hiding them.

## 6. Self-check before reporting

- Every requirement for this repo implemented; nothing extra.
- Every changed source file has its mirror test, and you can name the test covering each branch you added — nobody has run them yet, so this reading is the only check there is.
- Lint and the type check green on the final code.
- New files complete (`wc -l`, import check) — truncated files have shipped before.
- No import inside a function, method, or component in the diff — scan the added lines for your language's import form; if one is there, the fix is the cycle, not the placement.
- No secrets, no `.env`, no debug prints, no AI attribution anywhere.

## Output

Write the work log to `$WS/llm/scratchpad/plans/<TICKET>-<role>.md` — absolute path; your cwd is inside the worktree, and a relative `llm/scratchpad/` would create one inside the product repo. `<role>` is your role's `name` (`backend-dev`, `frontend-dev`).

Contents, and the same back to the orchestrator: branch · worktree path · files changed · **the exact node IDs of every test you wrote or changed**, and which changed source file each one mirrors · lint and type-check result (decisive line on failure) · the contract as actually implemented · anything you could not test without running something · anything from the plan not done and why.

**No test results** — you ran none. A work log claiming a green test run in this phase is wrong by construction.

## Stop conditions

Write a [`memory/`](../memory/README.md) entry when something failed for a reason the docs did not predict, or a green result turned out not to mean what it looked like — with the cost, which is why the next run reads it.

Stop and report instead of improvising when: the plan is missing something you need or contradicts the code; the work would touch another role's repo or one the workspace marks out of scope; the branch needs a dependency change you cannot make without breaking the shared environment; or lint fails for a reason that predates your diff.

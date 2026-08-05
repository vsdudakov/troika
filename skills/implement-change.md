---
name: implement-change
description: Implements one repo's part of an approved plan in its own worktree, with unit tests written but not run, ending at the profile's verification commands — no commit, no PR.
---

# Implement change (one repo)

One repo's share of an approved plan, in that repo's worktree, with the tests that prove it.

**Kind** procedure · **Used by** [backend-dev](../agents/backend-dev.md) · [frontend-dev](../agents/frontend-dev.md) · **When** the plan passes review (develop-flow step 3) · **Ends with** code written, tests written **and not run**, and every verification command the profile lists for the touched areas green — **not** a commit or PR; [release-pr.md](release-pr.md) does that after review, tests, and QA

Set `WS` first — every scratchpad path below is absolute ([AGENTS.md › Workspace paths](../../AGENTS.md#workspace-paths)).

## 1. Read the plan

`$WS/llm/scratchpad/plans/<TICKET>.md` — take only the requirements and work items for your repo. If something needed is missing or contradicts the code, stop and report; never re-plan silently.

## 2. Branch in a worktree — one per repo, not one per role

**First check whether this repo's worktree for the ticket already exists** — another role may already own this lane ([develop-flow › Lanes](develop-flow.md#lanes)):

```bash
git worktree list | grep "<repo>-<TICKET>"
```

- **It exists** → work in it, on its branch. Read that role's work log first (`$WS/llm/scratchpad/plans/<TICKET>-<role>.md`) and stay inside your own [ownership](../../AGENTS.md#ownership) paths. Never cut a second branch or worktree for a repo that already has one — one repo is one branch and one PR however many roles touch it.
- **It does not** → create it. `<BASE>` is the profile's base ref (remote plus default branch, e.g. `origin/main` — [AGENTS.md › Branches](../../AGENTS.md#branches)); the directory name `<repo>-<TICKET>` is a contract QA and release both depend on ([worktree › naming](worktree.md#naming)):

```bash
git fetch <remote>
git worktree add "$WS/llm/worktrees/<repo>-<TICKET>" -b <branch, per the profile> <BASE>
```

Wire up dependencies with the symlinks in [AGENTS.md › Branches](../../AGENTS.md#branches) — **do not reinstall** — using the absolute form (`"$WS/<repo>/…"`); the relative one is three or four `../` deep ([worktree › setup](worktree.md#setup)). Set signing per the profile's rules, once per worktree. Then index the worktree: it is its own root, and everything you search from here reads that index ([AGENTS.md › Code search](../../AGENTS.md#code-search)).

## 3. Implement

Follow the profile — [Rules](../../AGENTS.md#rules) · [Style](../../AGENTS.md#style) · [Layering](../../AGENTS.md#layering) — and your role file. No layer skipped; new code goes where that kind of code already lives; comments only for a non-obvious why.

**Imports go at the top of every file.** A circular-import error means the cycle is the bug: fix the direction, move the shared piece down a layer, or split the module — never defer the import into a function. None of those possible inside the plan's scope → stop and report.

Migrations: generate with the repo's command ([AGENTS.md › Commands](../../AGENTS.md#commands)) — never hand-edit an applied migration.

<a id="tests"></a>
## 4. Tests, with the code — written, not run

**You write the tests. You do not run them.** [tester](../agents/tester.md) runs them once, across every lane, in step 5 ([run-unit-tests](run-unit-tests.md)); CI runs the full suite on the PR. **You get no red-green loop**, so they must be right on the first pass — write them the way you would review them.

- **Every changed or created source file ships its mirror test**, at the path the profile fixes ([AGENTS.md › Tests](../../AGENTS.md#tests)).
- **Cover every branch you touched** — each guard, each `except`, each early return, each error state. No coverage report is in front of you; walk the diff line by line and name the test covering each one.
- Framework, naming, location, and what may be mocked are in [AGENTS.md › Tests](../../AGENTS.md#tests) — a spec and a gate.
- **Assert real behaviour**, not that the code was called. A blind test asserting a mock passes for the wrong reason.
- **Node IDs go in your work log** — exact paths and test names. The tester's selection starts from the diff and checks itself against your list.

Read your tests once more before reporting: a typo in a fixture or import costs a whole fix cycle in step 5.

<a id="verify"></a>
## 5. Verify — gate

**Run exactly the verification commands the profile lists for the areas you touched** ([AGENTS.md › Commands](../../AGENTS.md#commands)) — the full lint, plus a separate type check, build, or check target **only where the profile names one for that area**. Never invent a gate it does not list, never skip one it does. All green on the final code; they are the only automated signal you get, and a syntax error, bad import, type mismatch, or unused symbol in a test file surfaces here.

**No test command runs here**, targeted or otherwise.

**Never run a formatter or auto-fixing lint target in a worktree whose dependency directory is a symlink** — it walks the shared environment and rewrites it. Remove the symlink first, format from the primary clone, or use the profile's read-only variant ([AGENTS.md › Gotchas](../../AGENTS.md#gotchas)).

<a id="notests"></a>
### Why not run them here

A dev role running its own tests re-runs them every fix cycle, in series with the other lane, in an already long session. Step 5 runs them **once, across every lane at the same time**, from a diff-derived selection, after review has removed the defects a run would have found the slow way.

If a test cannot be written without running something — a fixture whose shape you cannot infer, a snapshot that must be generated — say so in the work log and hand the node ID to the tester. Do not turn that into a local suite run.

Pre-existing failures on the base branch are not yours to fix — name them in the report.

## 6. Self-check before reporting

- Every requirement for this repo implemented; nothing extra.
- Every changed source file has its mirror test, and you can name the test covering each branch you added — nobody has run them, so this reading is the only check there is.
- Every verification command the profile lists for your areas is green.
- New files complete (`wc -l`, import check) — truncated files have shipped before.
- No import inside a function, method, or component in the diff.
- No secrets, no `.env`, no debug prints, no AI attribution anywhere.

## Output

Write the work log to `$WS/llm/scratchpad/plans/<TICKET>-<role>.md` — absolute path; your cwd is inside the worktree, and a relative `llm/scratchpad/` would create one inside the product repo. `<role>` is your role's `name` (`backend-dev`, `frontend-dev`).

Contents, and the same back to the orchestrator: branch · worktree path (and whether you created or joined it) · files changed · **the exact node IDs of every test you wrote or changed**, and which source file each mirrors · the verification commands you ran and their results (decisive line on failure) · the contract as actually implemented · anything you could not test without running something · anything from the plan not done and why.

**No test results** — you ran none. A work log claiming a green test run in this phase is wrong by construction.

## Stop conditions

Write a [`memory/`](../memory/README.md) entry when something failed for a reason the docs did not predict, or a green result turned out not to mean what it looked like — with the cost.

Stop and report instead of improvising when: the plan is missing something you need or contradicts the code; the work would touch another role's paths or a repo the workspace marks out of scope; the branch needs a dependency change you cannot make without breaking the shared environment; or a verification command fails for a reason that predates your diff.

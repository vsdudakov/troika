# Troika

<img src="docs/assets/troika.jpg" alt="A troika — three horses harnessed abreast, pulling one sleigh" width="100%">

<sub>Nikolai Sverchkov (1817–1898), *A Troika Ride Through The Snow*. Public domain, via
[Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Nikolai_Sverchkov_-_A_Troika_Ride_Through_The_Snow.jpg).</sub>

**Troika turns a tracker ticket into a reviewed, QA-verified pull request.** An AI
coding-agent pipeline for full-stack developers — plan, implement, review, test, verify,
ship — with a gate at every step. Install it as a plugin for
[Claude Code](https://claude.com/claude-code),
[Codex](https://developers.openai.com/codex/cli/) or [Cursor](https://cursor.com), or run it
from plain markdown in any agent.

[![CI](https://github.com/vsdudakov/troika/actions/workflows/check.yml/badge.svg)](https://github.com/vsdudakov/troika/actions/workflows/check.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.md)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-d97757.svg)](#install)
[![Codex](https://img.shields.io/badge/Codex-plugin-10a37f.svg)](#install)
[![Cursor](https://img.shields.io/badge/Cursor-plugin-blue.svg)](#install)
[![Sponsor](https://img.shields.io/badge/sponsor-%E2%9D%A4-ec6cb9.svg?logo=github-sponsors)](https://github.com/sponsors/vsdudakov)

📖 **Documentation: [vsdudakov.github.io/troika](https://vsdudakov.github.io/troika/)**

Troika is an **agentic development pipeline**: eight specialised roles — architect,
backend and frontend developers, reviewer, tester, QA, releaser, commenter — that take a
ticket from your tracker and hand back a pull request with proofs attached. It automates the
whole loop a full-stack developer runs by hand: requirements and planning, parallel
implementation in git worktrees, **automated code review**, unit tests, **QA verification on
your real local stack**, the release PR, and the CI and review-bot watch after it. Release
cuts, **release notes** and demo builds are in the box too.

It is not a framework and not a runtime: it is **plain markdown** — roles, procedures and
templates — that any coding agent loads by path, wired into slash commands for the three
hosts that ship a plugin system.

One command runs the whole pipeline:

```
/troika:dev SCRUM-123
```

Behind it: the architect plans, a **different model family** reviews the plan and loops it
back, dev roles implement in parallel worktrees, the reviewer runs nine checks on the diff,
the tester runs only the tests the change developed, QA verifies on your real local stack
with before/after proofs, and the releaser opens the PR and watches CI. Each role runs in its
own context and hands off through files — never shared memory — so nothing downstream
inherits an earlier role's assumptions.

**Nothing in this repository names your organisation.** No repo, command, branch, tracker,
URL, or person. Every such fact comes from one file you write once — `AGENTS.md` in your
workspace — and every path comes from `.troika.json` beside it. Drop Troika into another
workspace, write those two files, and the same pipeline runs unchanged.

---

## Highlights

- 🚦 **Gates, not vibes.** Every step is a gate: a plan is not approved until a reviewer on a
  different model family approves it, a diff is not pushed until nine checks pass, a PR is
  not done until CI is green and the review bots are quiet.
- 🧑‍🤝‍🧑 **Eight roles, eight contexts.** architect · backend-dev · frontend-dev · reviewer ·
  tester · qa · releaser · commenter — each with its own scope, model, effort, and hard
  refusals. Dev roles write tests but never run them; the reviewer never runs anything.
- 🔌 **One tree, three hosts.** The same skills are `/troika:*` commands in Claude Code and
  Cursor, and model-invoked skills in Codex. Or skip the plugin and point any agent at the
  files by path.
- 🏢 **Organisation-neutral by construction.** Org facts live in your `AGENTS.md` profile and
  are linked **by anchor**; a procedure that hardcodes one is a bug, and CI fails it.
- 📂 **Per-workspace paths.** `.troika.json` says where plans, worktrees and memory live —
  one file per folder-of-repos, so a single installed plugin serves every client and org you
  work in.
- 🧪 **It is tested on itself.** A structural gate checks every link, anchor, and file shape;
  a behavioural gate plants seventeen known defects in a toy repo and asserts the role that
  claims to catch each one does.

## Install

Troika works two ways, and they compose: **clone** it into a workspace (the roles read it by
path — works in any agent, including ones with no plugin system), and optionally **install**
it as a plugin for the `/` commands.

**Claude Code**

```bash
claude plugin marketplace add vsdudakov/troika
claude plugin install troika@troika          # add --scope project to pin it to one workspace
```

**Codex**

```bash
codex plugin marketplace add <path to a local clone>
codex plugin add troika@troika
```

**Cursor**

```bash
cursor-agent plugin marketplace add https://github.com/vsdudakov/troika
```

**No plugin at all** — clone it and ask your agent to read a file:

```bash
git clone https://github.com/vsdudakov/troika
```

```
read troika/skills/develop-flow/SKILL.md and run it for SCRUM-123
```

## Set up a workspace

A *workspace* is the folder holding your repos. It needs two files.

**1. `AGENTS.md`** — the project profile. Copy [`AGENTS.template.md`](AGENTS.template.md) and
fill every section: which repos exist, who owns what, the exact verification commands, the
base branch, the tracker, the local stack, the PR template, the release scheme. The
**anchors are a contract** — roles link to them by name (`#commands`, `#branches`,
`#tracker`, …) and a missing one is a role reading a dead link. `python3 tests/check.py`
verifies every anchor the tree needs exists in the template.

Where the profile declares a *limit* — no ticket transitions, one repo and one PR, no build
step, a base branch that is not `origin/main` — the roles follow the profile, not the generic
wording.

**2. `.troika.json`** — where this workspace keeps its files. Every key is optional, relative
paths resolve against the file, and absolute ones are taken as-is:

```json
{
  "profile": "AGENTS.md",
  "home": "troika",
  "scratchpad": "troika/scratchpad",
  "worktrees": "/Volumes/fast/acme/worktrees",
  "memory": "troika/memory"
}
```

```
<workspace>/
  AGENTS.md      the project profile — yours, org-specific
  .troika.json   where this workspace keeps its files
  troika/        this repo — generic, shared across workspaces
  <repos…>       your product repos, each an independent clone
```

Roles run with their cwd deep inside a worktree, so they never guess a path — they resolve
one:

```bash
eval "$(python3 troika/plugin/resolve.py)"
# exports WS, TROIKA_PROFILE, TROIKA_HOME, TROIKA_WORKTREES, TROIKA_SCRATCHPAD, TROIKA_MEMORY
```

The resolver walks up from wherever the role is standing to the workspace that owns it, so
one installed plugin serves every workspace on the machine. See
[plugin/README.md](plugin/README.md#configuring-a-workspace).

## The pipeline

[`develop-flow`](skills/develop-flow/SKILL.md) is the whole thing. Nine steps, each a gate:

| Step | What happens | Who |
| --- | --- | --- |
| 0 | Fan out — refresh the code index, read the ticket, read memory | orchestrator |
| 1 | Collect requirements, write the plan | [architect](agents/architect.md) |
| 2 | **Plan review loop** — a different model family approves or sends it back (cap 3 rounds) | [reviewer](agents/reviewer.md) |
| 3 | Development — one lane per repo, own worktree, tests written but not run | [backend-dev](agents/backend-dev.md) · [frontend-dev](agents/frontend-dev.md) |
| 4 | **Internal review loop** — nine checks on the local diff, lint only, nothing posted | [reviewer](agents/reviewer.md) |
| 5 | Unit tests — the change's own tests only, parallel lanes, failures routed back | [tester](agents/tester.md) |
| 6 | **QA on the real local stack** — browser E2E with before/after GIFs, API + datastore checks | [qa](agents/qa.md) |
| 7 | Release — commit, push, PR from your template with proofs, ticket updated | [releaser](agents/releaser.md) |
| 8 | CI + review-bot watch loop — the PR is not done until it is quiet | [releaser](agents/releaser.md) |

Every outward-facing sentence on the way — PR body, ticket comment, review reply — is written
by the [commenter](agents/commenter.md) in your workspace's voice.

Or start somewhere else:

```
/troika:spike SCRUM-123              # investigate and plan it, build nothing
/troika:review 412                   # review an open PR
/troika:qa https://github.com/<org>/<repo>/pull/412
/troika:triage <stack trace>
/troika:release 2026.8.0             /troika:demo
```

Seven commands, and every other procedure — plan-review, implement-change, internal-review,
run-unit-tests, release-pr, release-notes, ticket-intake — is still a skill all three hosts
discover, invocable by name when you want just that step.

## What is in the box

| | |
| --- | --- |
| [`agents/`](ROLES.md) | the eight roles — scope, inputs, rules, gates, output, and the model and effort each runs on |
| [`skills/`](skills/README.md) | 14 procedures, 5 references, 2 templates — one directory per skill, `SKILL.md` inside |
| [`plugin/`](plugin/README.md) | the three host manifests, the generated commands, and [`resolve.py`](plugin/resolve.py) |
| [`tests/`](tests/README.md) | the two gates on this tree |
| [`AGENTS.template.md`](AGENTS.template.md) | the profile you fill in, and the anchor contract |

Procedures: `develop-flow` · `spike` · `plan-review` · `implement-change` ·
`internal-review` · `run-unit-tests` · `qa-verify` · `release-pr` · `pr-review` ·
`ticket-intake` · `incident-triage` · `demo-prep` · `release-cut` · `release-notes` — seven
of them carry a `/` command, the rest are skills you name. References: `worktree` ·
`scratchpad` · `memory` · `cross-repo` · `tracker`. Templates: `plan-template` ·
`pr-template`.

Plans, proofs, worktrees and memory are **not in this repository at all** — they are
per-workspace, ignored whole, and created wherever your `.troika.json` puts them by
`python3 plugin/resolve.py --ensure`. Because they are *ignored* rather than absent,
`git clean -xfd` here deletes all three, in-flight branches included. Clean with explicit
paths or not at all.

## How it stays honest

You cannot unit-test a prompt. You *can* test a gate — and both gates run on this repo in CI.

```bash
python3 tests/check.py          # structural: seconds, every commit
python3 tests/run.py --runs 5   # behavioural: real model runs, catch rate per case
```

[`check.py`](tests/check.py) asserts every link and anchor resolves, the profile anchors
exist in the template, the file shapes match what the READMEs declare, the reviewer's check
list matches its copies, the `/` commands are current, and that no file hardcodes a path the
workspace is allowed to move.

[`run.py`](tests/run.py) is the interesting one: `fixtures/repo` is a tiny layered app,
`cases/_base` implements its plan **correctly**, and each of seventeen cases is that base
plus exactly one planted defect — a deferred import, a skipped layer, an N+1, a test that
asserts nothing, a secret, a work log that overstates its test count. The gate that claims to
catch each one has to catch it. Two of the seventeen are controls: a clean diff must come
back approved, and a diff whose only problems are nits must not be blocked. A gate that flags
everything is worthless, and the controls are what prove it isn't.

Change a role file and measure what it cost you:

```bash
python3 tests/run.py --runs 5 > /tmp/before.txt   # on the old revision
python3 tests/run.py --runs 5 > /tmp/after.txt    # on the new one
diff /tmp/before.txt /tmp/after.txt
```

## Why Troika

Most agent setups are one long prompt and a lot of hope. Troika splits the work the way a
team does — someone plans, someone else reviews the plan, someone implements, someone else
reviews the diff, someone runs the stack — and makes each handoff a file with a fixed shape.
That buys three things a single context cannot: a reviewer that never saw the author's
reasoning, a QA pass that runs against your real stack instead of a summary of it, and a
failure that names the step it happened in.

It is deliberately **not** a framework. There is no runtime, no daemon, no vendor lock: it is
markdown your agent reads, so you can fork a role, delete a step, or run one procedure by
hand — and a Python script under 200 lines is the only executable in the critical path.

## Conventions

Roles run in separate contexts and hand off through files, never shared memory — the
[handoff contract](ROLES.md#handoff).

**Absolute paths.** Every role's cwd is inside a worktree, so `$TROIKA_SCRATCHPAD` is not
below it. Resolve the paths once per session ([Set up a workspace](#set-up-a-workspace)) and
use them verbatim; a relative path writes a file no later role finds.

<a id="shell-quoting"></a>
**Posting text through a shell.** Findings and PR bodies contain backticks, `$`, and quotes;
inside `"…"` the shell executes backticks as command substitutions and silently drops the
result. Always pass generated text through a quoted heredoc, never a double-quoted argument:

```bash
gh pr comment 42 --body "$(cat <<'EOF'
- **Major** `service/portfolio.py:88` — N+1 · use `select_related`
EOF
)"
```

The same applies to `gh pr create --body`, any tracker CLI's comment command, and
`git commit -m`.

**File shape.** Every role and skill opens with `name` and `description` frontmatter — the
one convention all three hosts read. Roles then carry a fixed header list and five sections
(`Scope` · `Inputs` · `Rules` · `Gates` · `Output`); skills carry a one-line header and
follow their kind's body shape. [`ROLES.md`](ROLES.md) and
[`skills/README.md`](skills/README.md) declare both, and `check.py` enforces them.

## Development

```bash
git clone https://github.com/vsdudakov/troika
cd troika
python3 tests/check.py              # structural gate — no model, no spend
python3 tests/run.py --check        # fixtures only — no model, no spend
python3 plugin/generate.py          # regenerate the / commands after editing a procedure
```

Editing a procedure? Its frontmatter drives the command that runs it, so regenerate and let
`check.py` confirm nothing drifted. Adding a role? It goes in `agents/` — and *only* roles go
there, because hosts load every file in that directory as a subagent, which is why the roles
index lives at [`ROLES.md`](ROLES.md).

## Contributing

Issues and pull requests are welcome. Run `make check` and `make test-check` before opening
one; both must be green. If you change a role's rules or a procedure's gates, run the
behavioural suite with `make test RUNS=5` and put the catch rates in the PR — that is the only
evidence that matters here. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Sponsor

Troika is MIT-licensed and developed in the open. If it saves your team time, please consider
[**sponsoring on GitHub**](https://github.com/sponsors/vsdudakov). Every bit helps and is
hugely appreciated. ❤️

## License

[MIT](LICENSE.md) © Troika contributors

---
title: Skills
description: Procedures, references and templates — what each kind is for, the shape it must have, and how a skill becomes a slash command.
---

# Skills

A skill is one directory holding one `SKILL.md`. That is the shape Claude Code, Codex and
Cursor all discover a skill in, so the procedure is the file the host loads — no wrapper, no
second copy.

```
skills/
  develop-flow/SKILL.md
  qa-verify/SKILL.md
  worktree/SKILL.md
  …
```

## Three kinds

Every skill declares its `**Kind**`, and the kind fixes the body shape.

| Kind | Body | Read it as |
| --- | --- | --- |
| **procedure** | numbered `## 1.` … steps, then `## Output`, `## Stop conditions` | every step is a gate — do not advance until it holds |
| **reference** | topic sections, then `## Gotchas` | look up what you need |
| **template** | `## Fill rules`, then `## Template` | copy the block, fill it, delete what does not apply |

**Procedures** (13): `develop-flow` · `plan-review` · `implement-change` · `internal-review` ·
`run-unit-tests` · `qa-verify` · `release-pr` · `pr-review` · `ticket-intake` ·
`incident-triage` · `demo-prep` · `release-cut` · `release-notes`

**References** (5): `worktree` · `scratchpad` · `memory` · `cross-repo` · `tracker`

**Templates** (2): `plan-template` · `pr-template`

## Only procedures become commands

A `/troika:<name>` command exists for each **procedure** and nothing else — a reference is
read *by* a procedure, and a template is filled by one; neither can be "finished", so neither
should appear in a menu of things to run.

The commands are generated from the procedure's own frontmatter:

```bash
python3 plugin/generate.py
```

`check.py` fails if a command is stale, missing, or orphaned by a deleted procedure — an
orphan still shows in the `/` menu and sends the model to read a file that is gone.
[Adding a skill :material-arrow-right:](../guides/adding-a-skill.md)

## Every step is a gate

A procedure is not a checklist to skim. Its steps are ordered because each one's output is the
next one's input, and its `## Stop conditions` say when to stop rather than improvise. When a
step cannot be completed — a command the profile does not define, a stack that will not boot,
a proof that cannot be captured — the procedure stops and says so. It never substitutes a
weaker step and reports success.

## Skills contain no organisation facts

A skill says *"run the profile's verification commands"*, never `pytest -q`. It says *"the
base ref from the profile"*, never `origin/main`. That is what lets the same procedure run in
a workspace with one repo and no tracker, and in a workspace with six repos and a strict
transition policy. Facts come from [`AGENTS.md`](../guides/profile.md) by anchor.

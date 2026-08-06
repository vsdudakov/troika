---
title: Running without a plugin
description: Troika is markdown. Any agent that can read a file can run the pipeline — here is how, and what you give up.
---

# Running without a plugin

The plugin layer is a convenience. Everything it adds is a shortcut to *"read this file and
follow it"*, so any agent that can read a file can run Troika — including hosts with no plugin
system, CI jobs, and one-off scripted runs.

```bash
git clone https://github.com/vsdudakov/troika
```

```
read troika/skills/develop-flow/SKILL.md and run it for SCRUM-123
```

## Do the resolver step yourself

The commands normally run the resolver first. Without them, create the workspace once:

```bash
python3 troika/plugin/resolve.py --init <workspace>
```

and export the paths once per session:

```bash
eval "$(python3 troika/plugin/resolve.py --ensure)"
```

`--init` writes `.troika/settings.json`, its `.gitignore` and the state directories. The
profile is the part that needs reading and asking, so either run `/troika:setup` in a host that
has commands, or copy `troika/PROFILE.template.md` to `<workspace>/.troika/PROFILE.md` and fill
every anchor by hand.

Then the procedures' `$TROIKA_SCRATCHPAD`, `$TROIKA_WORKTREES` and `$TROIKA_MEMORY` references
resolve, and handoff files land where the next role will look.

## Run one role

```
read troika/agents/qa.md and verify SCRUM-123 on the local stack
read troika/agents/reviewer.md and run troika/skills/internal-review/SKILL.md on the branch diff
```

Give the role its `Inputs` — the plan file, the work log, the diff — the same way the pipeline
would. The role file states exactly what it expects.

## Non-interactive runs

Both CLIs read a prompt on stdin and write the reply to stdout, which is all the behavioural
suite needs:

```bash
claude -p --model claude-fable-5 --effort high  < prompt.txt
codex exec -m gpt-5.6-sol -                     < prompt.txt
```

This is how `tests/run.py` drives its cases, and it is a workable shape for a scheduled job —
nightly `pr-review` on open PRs, for example.

## What you give up

- **The `/` menu.** You type a path instead of a command name.
- **Subagent registration.** Roles run in whatever context you launch them in, so you have to
  keep them separate yourself — one role per session — or you lose the independence the
  handoff contract is built on.
- **Automatic path resolution.** One `eval` per session, as above.

Nothing else. The gates, the file shapes, the review checks and the handoff contract are all
in the markdown.

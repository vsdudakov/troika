---
title: Your first ticket
description: Run the whole pipeline on one ticket, see what each gate produces, and know where to look when one of them stops.
---

# Your first ticket

With a profile written and paths resolved, one command runs everything:

```
/troika:dev SCRUM-123
```

Start with a **small, well-specified ticket** in a repo whose profile section you trust. The
pipeline is only as sharp as the facts you gave it, and the first run is as much a test of
`AGENTS.md` as of the change.

## What you will see

| Stage | What lands on disk |
| --- | --- |
| Plan | `$TROIKA_SCRATCHPAD/plans/SCRUM-123.md` |
| Plan review | `…/SCRUM-123-plan-review-1.md` — `Approve`, or findings and a rewrite |
| Development | a worktree per repo at `$TROIKA_WORKTREES/<repo>-SCRUM-123`, plus `…/SCRUM-123-backend-dev.md` |
| Internal review | `…/SCRUM-123-review-1.md` — severity-tagged findings |
| Tests | `…/SCRUM-123-tests-1.md`, plus a raw `.log` per lane |
| QA | `…/SCRUM-123-qa-1.md` and `$TROIKA_SCRATCHPAD/proofs/SCRUM-123/` |
| Release | a branch, a PR with proofs attached, the ticket updated |

Numbered files are never overwritten: cycle 2 is a new file, so what was rejected stays
readable. [The scratchpad](https://github.com/vsdudakov/troika/blob/main/skills/scratchpad/SKILL.md)
documents every name.

## When it stops

It is supposed to stop. A gate that fails is the product working:

- **Plan review sends it back** — the plan was ambiguous or missed a requirement. It rewrites
  and re-reviews, up to three rounds, then asks you.
- **The reviewer files a Blocker** — the fix goes back to the dev role, and the re-review is a
  new numbered file. No diff advances unreviewed.
- **QA fails** — a proof could not be captured, or behaviour did not match the requirement.
  Fix, re-verify.
- **The resolver exits non-zero** — nothing ran. You are standing outside any workspace, or
  `.troika.json` is missing; see [Paths](../concepts/paths.md).

## Start somewhere else instead

Nothing requires the full pipeline. The other seven commands each start a session of their own:

```
/troika:spike   SCRUM-123     # investigate and plan it, and stop — nothing gets built
/troika:review  412           # review an open PR
/troika:fix     412           # fix that review's comments — or say what to fix instead
/troika:qa      412           # verify an open PR on your local stack, with proofs
/troika:triage  <paste a stack trace or an issue link>
/troika:release 2026.8.0
/troika:demo
```

The steps in between — `plan-review`, `implement-change`, `internal-review`,
`run-unit-tests`, `release-pr`, `release-notes`, `ticket-intake` — have no `/` entry, because
starting on one out of order is usually a mistake. They are still skills every host
discovers, so ask for one by name when you do mean it:

```
run internal-review on this branch
run ticket-intake for the Q3 export work
```

[Every command :material-arrow-right:](../reference/commands.md){ .md-button }

## Tune it afterwards

The first run tells you where the profile is thin. Typical fixes, in order of payoff:

1. **`#commands`** — if a dev role ran something that is not a gate, or skipped one that is.
2. **`#tests`** — if the reviewer could not tell what a mirror test should look like.
3. **`#stack`** and **`#stack-limits`** — if QA could not bring the stack up, or verified
   something the local stack cannot actually prove.
4. **`#gotchas`** — anything that surprised a role. If it will surprise the next one, it is a
   gotcha; if it might expire, it is
   [memory](https://github.com/vsdudakov/troika/blob/main/skills/memory/SKILL.md) instead.

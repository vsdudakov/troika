---
title: Your first ticket
description: Run the whole pipeline on one ticket, see what each gate produces, and know where to look when one of them stops.
---

# Your first ticket

With a profile written and paths resolved, one command runs everything:

```
/troika:develop-flow SCRUM-123
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

## Run one piece instead

Nothing requires the full pipeline:

```
/troika:ticket-intake   make a ticket for the Q3 export work
/troika:plan-review     SCRUM-123
/troika:internal-review SCRUM-123
/troika:qa-verify       SCRUM-123
/troika:release-pr      SCRUM-123
/troika:pr-review       412
/troika:incident-triage <paste a stack trace or an issue link>
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

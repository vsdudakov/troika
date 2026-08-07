---
title: Your first ticket
description: Run the whole pipeline on one ticket, see what each gate produces, and know where to look when one of them stops.
---

# Your first ticket

With a profile written and paths resolved, one command runs everything:

```
/tr:dev SCRUM-123
```

Start with a **small, well-specified ticket** in a repo whose profile section you trust. The
pipeline is only as sharp as the facts you gave it, and the first run is as much a test of
the profile as of the change.

## What you will see

The first thing it decides is the ticket's **kind**, and that picks the next two steps: a bug
is reproduced on the base checkout before anyone fixes it, a feature is planned and the plan
is reviewed. Everything from development on is the same either way.

| Stage | What lands on disk |
| --- | --- |
| Plan, or bug brief | `$TROIKA_SCRATCHPAD/plans/SCRUM-123.md` |
| Plan review *(feature)* | `…/SCRUM-123-plan-review-1.md` — `Approve`, or findings and a rewrite |
| Reproduction *(bug)* | `…/SCRUM-123-repro-1.md` — `Reproduced`, plus the failing capture, which is reused as the `before` proof |
| Reporter review | nothing on disk — one message to the reporter, and their answer recorded in the plan file. Only on a `--ask` run |
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
- **The reporter says "change this"** — what you asked for was not what the plan or the
  reproduction describes. It goes back to the plan or the brief, twice at most, then hands back
  to you. This is the only gate that waits for a person, and it exists only on a `--ask` run —
  a plain `/tr:dev SCRUM-123` never stops for an approval.
- **The bug does not reproduce** — the reporter's steps produced the expected behaviour on the
  base checkout. It stops rather than fixing blind, and says what it ran and what it needs from
  the reporter: an environment, a data shape, a user role.
- **The reviewer files a Blocker** — the fix goes back to the dev role, and the re-review is a
  new numbered file. No diff advances unreviewed.
- **QA fails** — a proof could not be captured, or behaviour did not match the requirement.
  Fix, re-verify.
- **The resolver exits non-zero** — nothing ran. You are standing outside any workspace, or
  `.troika/settings.json` is missing — run `/tr:setup`; see [Paths](../concepts/paths.md).

## Start somewhere else instead

Nothing requires the full pipeline. The other seven commands each start a session of their
own — this is roughly how a team splits them up:

```
# a developer, on an assigned ticket
/tr:dev     SCRUM-123     # the whole pipeline
/tr:dev     SCRUM-123 --ask    # ... stopping once for the reporter's approval
/tr:spike   SCRUM-123     # investigate and plan it, and stop — nothing gets built

# the same developer, once the PR is open — always the same branch, never a second PR
/tr:fix     https://github.com/<org>/<repo>/pull/41
/tr:fix     https://github.com/<org>/<repo>/pull/41 stream the export instead of buffering it

# developers, on each other's PRs
/tr:review  https://github.com/<org>/<repo>/pull/41   # nine checks, one posted comment
/tr:qa      https://github.com/<org>/<repo>/pull/41   # local stack, before/after proofs, Pass or Fail

# anyone, on a production symptom
/tr:triage  <paste a stack trace or an issue link>

# the release manager
/tr:demo    release/X.Y.Z # build and deploy the demo integration branch
/tr:release release/X.Y.Z # promote, branch, notes, QA plan, pre-production deploy
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

---
name: spike
description: Investigates a ticket read-only and produces a reviewed implementation plan — the pipeline's planning half, stopped before any code is written.
---

# Spike (investigate and plan, no code)

A ticket link in, an approved plan out. Nothing is implemented, branched, or committed.

**Kind** procedure · **Used by** [architect](../../agents/architect.md) · **When** a ticket needs sizing, shaping or a design decision before anyone commits to building it · **Ends with** an approved plan at `$TROIKA_SCRATCHPAD/plans/<TICKET>.md` and a summary, with no worktree and no code

This is [develop-flow](../develop-flow/SKILL.md) steps 0, 1f and 2f — its **feature** path's planning half — and nothing after them. A spike plans even where the ticket is a bug: the answer wanted is a shape and a cost, and reproducing it belongs to the flow that will fix it ([Kind](../develop-flow/SKILL.md#kind)). Run it when the answer wanted is *what would this take* rather than *ship it*; when the plan is approved and the work is wanted, [develop-flow](../develop-flow/SKILL.md) picks up the same plan file at its step 3.

Read-only over every repo. Set `TROIKA_WORKSPACE` first (workspace paths (`#workspace-paths`)).

## 1. Fan out — index, ticket, memory, all at once

Start together; join before investigating:

1. Refresh each repo index from its root (code search (`#code-search`)).
2. Read every ticket surface — description, comments, attachments, links, fields ([ticket surfaces](../plan-review/SKILL.md#ticket-surfaces)). The argument is a ticket key or link; auth and access per PROFILE.md › Tracker (`#tracker`) and [tracker](../tracker/SKILL.md). A ticket key uses the profile's casing — a false "missing" issue usually means stale auth, not a missing ticket.
3. Run `ls $TROIKA_MEMORY/*.md`; read every entry ([memory](../memory/SKILL.md)).

If the request arrives as prose with no ticket behind it, run [ticket-intake](../ticket-intake/SKILL.md) first and spike the ticket it produces.

## 2. Investigate the code — read-only, one probe per area

Fan out reading, not decisions: one read-only probe per repo or area, each answering the same three questions with `file:line` evidence.

| The probe reports | Why the plan needs it |
| --- | --- |
| Where the behavior lives today | a plan pinned to a symbol that moved is wrong before dev starts |
| The shape it is built in — layers, ownership, migrations | it decides the repo split and the dependency order (`#dependency-order`) |
| What already covers it in tests | it decides which requirements need new tests and which need QA proof |

Probes read; they never edit, branch, or run the local stack (`#stack`). The [architect](../../agents/architect.md) synthesizes them — a probe that proposes a design has exceeded its scope.

Name every repo the change touches, including ones no role owns. An unowned repo is a finding, not a blocker to hide.

## 3. Write the plan

The architect writes `$TROIKA_SCRATCHPAD/plans/<TICKET>.md` per [plan-template.md](../plan-template/SKILL.md) — numbered requirements, repo order, pinned cross-repo contracts, the test plan, risks and open questions.

Two things this plan carries that a mid-flow plan does not:

- **Cost.** Rough size per repo lane and what dominates it, so the plan can be scheduled or dropped.
- **Alternatives considered.** Under risks: what else was on the table and why it lost. A spike whose only output is one design has answered a narrower question than the one asked.

## 4. Plan review + rewrite loop — gate, no human

Run [plan-review.md](../plan-review/SKILL.md) with [reviewer](../../agents/reviewer.md), using a **different model family** from the architect ([runner](../plan-review/SKILL.md#runner)).

1. Check ticket coverage, testability, symbols, ownership, contracts, tests, assumptions.
2. Blocker/Major → architect rewrites `<TICKET>.md`; re-review.
3. Cap at 3 cycles; then stop and report.

Each pass writes `$TROIKA_SCRATCHPAD/plans/<TICKET>-plan-review-<n>.md`.

Ask the human only for scope or behavior with no safe assumption, unowned scope, undefined completion, or a hit cap ([human](../plan-review/SKILL.md#human)).

**No separate reporter review here.** A spike's whole output is a plan handed to the person who asked for it, so [develop-flow's 2r gate](../develop-flow/SKILL.md#reporter-review) would be the same conversation twice. When that plan is later built, develop-flow runs 2r on it only if that run carries `--ask` ([Autonomy](../develop-flow/SKILL.md#autonomy)); a plan a reporter already answered on carries that answer in its file and 2r reads it rather than asking again.

<a id="no-transition"></a>
**Make no tracker write here** — no comment, and in particular **no in-progress transition**, even where the profile declares one. plan-review runs that transition on `Approve` because in develop-flow the code starts immediately; here nothing starts, and a ticket parked in progress with no branch behind it is a lie the board acts on. Where the plan should reach the tracker, say so in the summary and let the human ask for it.

## Output

The plan file and its review passes, plus a summary returned to the caller:

```markdown
### Spike: <TICKET>
- Sources read: description · comments (<count>) · attachments (<count>, viewed) · links (<count>, followed) · fields — <anything unreachable, named>
- Repos touched: <repo — what changes there · …> — <any unowned, named>
- Plan: `$TROIKA_SCRATCHPAD/plans/<TICKET>.md` — <Approve | Approve with nits | Request changes> after <n> review cycle(s)
- Size: <rough cost per lane, and what dominates it>
- Alternatives rejected: <option — why>
- Open questions for the human: <question, or none>
- Next: run develop-flow for <TICKET> to build it — nothing was implemented
```

Internal only. No branch, no worktree, no commit, no PR, no tracker write.

## Stop conditions

Stop and report when: the ticket cannot be read ([tracker](../tracker/SKILL.md)); the review cap in step 4 is hit; the plan needs a repo no role owns; the ticket needs a product decision nobody has made ([human](../plan-review/SKILL.md#human)); or the investigation shows the ticket is already done, obsolete, or a duplicate — say so and stop rather than planning work nobody needs.

Never write product code in this procedure. A "tiny fix while I was in there" is the one failure this skill exists to prevent: it lands unreviewed, untested, and outside any branch the flow tracks.

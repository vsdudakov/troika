---
name: plan-template
description: The structure of an approved plan — problem, numbered requirements, repo order, pinned contracts, per-repo work breakdown, test plan, risks and open questions — and the shorter bug brief the reproduction path writes instead.
---

# Plan template

Trusted plan; no downstream product decisions required.

**Kind** template · **Used by** [architect](../../agents/architect.md) · **When** the ticket is understood and the code is read (develop-flow step 1f, or 1b for the [bug brief](#bug-brief)) · **Ends with** `$TROIKA_SCRATCHPAD/plans/<TICKET>.md`, ready for the [plan-review](../plan-review/SKILL.md) gate or the [reproduction](../qa-verify/SKILL.md#reproduce) gate

**One file, two shapes.** A feature ticket fills the full template below and is approved by plan review. A bug ticket fills the shorter [bug brief](#bug-brief) and is approved by a reproduction on the base checkout. Both are written to the same path, because every later role — reviewer, tester, qa, releaser — reads the requirements from `plans/<TICKET>.md` and must not care which path produced them.

## Fill rules

- Delete sections that don't apply; never leave a placeholder in.
- Requirements are numbered and testable — every later role cites them by number, so the numbers stay stable across rewrites.
- Repo order follows PROFILE.md › Dependency order (`#dependency-order`).
- Pin cross-repo contracts or mark sequential.
- Map every requirement to unit/QA proof.
- Name stack limits and alternate coverage.
- Make out-of-scope explicit, including forbidden repos.
- Block on scope/behavior questions; record other assumptions for PR body.

## Template

````markdown
# <TICKET> — <title>

Ticket: <link>
Status: draft | awaiting approval | approved <date>
Reporter: <their answer at 2r — "go ahead <name>, <date>", or "not asked — auto">

## Problem
<2–4 sentences: what is broken or missing, for whom.>

## Requirements
1. <testable statement — what the system must do after the change>
2. …

## Out of scope
- <explicitly not doing>
- <repo the workspace keeps out of scope> — never touched.

## Repos and order
| # | Repo | Work | Depends on | Parallel with |
|---|------|------|------------|---------------|
| 1 | <provider> | … | — | — |
| 2 | <service>  | … | 1 | — |
| 3 | <client>   | … | contract from 2 | 2 (contract pinned) |

## Contracts
<Exact shared shapes. One block per endpoint/event/schema.>

`GET /api/v1/<path>` → 200
```json
{ "field": "type — meaning" }
```
Errors: 400 <when>, 404 <when>.

## Work breakdown
### <repo>
- Layer path: <entry point> → <service> → <storage> → <model>
- Migration: yes/no — <what changes>
- Tests: <path per the workspace's test convention> — <cases>

### <client repo>
- Files: <folder>/<file>
- Tests: <name>.test.<ext> — <cases>

## Test plan
| Requirement | Unit test | QA on local stack |
|---|---|---|
| 1 | <file::test> | <click path or API call, expected result> |

Not verifiable on the stack: <requirement> — covered by <what instead>.

## Risks
- <risk> · mitigation: <…>

## Open questions
- [ ] <question for the human — blocks approval>
- Assumed: <ambiguity resolved by judgment, recorded here and repeated in the PR body>
````

<a id="bug-brief"></a>
## The bug brief — the same file, on the bug path

Written at [develop-flow step 1b](../develop-flow/SKILL.md#kind), before the bug has been reproduced, and corrected at step 2b by what the reproduction actually showed. It is short on purpose: the evidence is the reproduction, not the prose.

Same fill rules, plus three of its own:

- **The steps are the reporter's**, verbatim, in their order. Steps you improved go in a separate list, marked as yours — [qa-verify › Reproduction](../qa-verify/SKILL.md#reproduce) runs the reporter's first.
- **Observed and expected are separate lines.** A brief that states only what should happen has not written down the bug.
- **Every fix requirement names its regression test** — the reproduced failure expressed as a test at the layer the cause lives in. A fix with no such test is stopped at internal review.

````markdown
# <TICKET> — <title>

Ticket: <link>
Kind: bug
Status: awaiting reproduction | reproduced <date> | reproduced differently <date>
Reporter: <their answer at 2r — "go ahead <name>, <date>", or "not asked — auto">

## Reported
<2–4 sentences in the reporter's terms. Who hit it, how often, what it blocks.>

## Environment
<ref or version · browser or client · user role · feature flags · data shape the bug needs>

## Steps to reproduce
1. <the reporter's step>
2. …

<Derived by us — say so, and why the ticket had none:>
1. <derived step>

## Observed
<what happens now — the error text, the wrong value, the missing row, the trace.>

## Expected
<what should happen instead, and the source that says so: ticket, spec, adjacent behaviour.>

## Cause
<file:line, from the read-only probes. "Not located yet" is an honest value before step 2b.>

## Fix requirements
1. <testable statement — what the system must do after the fix> · regression test: <path::test>
2. …

## Out of scope
- <the adjacent defect this ticket is not> — <where it was filed instead, or that it was not>

## Repos and order
| # | Repo | Work | Depends on |
|---|------|------|------------|
| 1 | <repo> | … | — |

## Test plan
| Requirement | Regression test | QA on local stack |
|---|---|---|
| 1 | <file::test> — fails on the base ref for the reported reason | <the reproduction steps, re-run on the branch> |

## Risks
- <what this fix could break> · mitigation: <…>
````

---
name: plan-template
description: The structure of an approved plan — problem, numbered requirements, repo order, pinned contracts, per-repo work breakdown, test plan, risks and open questions.
---

# Plan template

The one artifact every later role trusts: concrete enough that a dev role makes no further product decisions.

**Kind** template · **Used by** [architect](../agents/architect.md) · **When** the ticket is understood and the code is read (develop-flow step 1) · **Ends with** `$WS/llm/scratchpad/plans/<TICKET>.md`, ready for the human approval gate

## Fill rules

- Delete sections that don't apply; never leave a placeholder in.
- Requirements are numbered and testable — every later role cites them by number.
- Repo order follows [AGENTS.md › Dependency order](../../AGENTS.md#dependency-order).
- Every cross-repo boundary gets a pinned contract, or the repos are marked sequential ([cross-repo](cross-repo.md)).
- Every requirement gets at least one test: a unit test, a QA step, or both.
- Anything the local stack cannot exercise ([AGENTS.md › Stack limits](../../AGENTS.md#stack-limits)) is named here, with what covers it instead.
- Out of scope is explicit, and names any repo the workspace keeps out of every role's reach ([AGENTS.md › Ownership](../../AGENTS.md#ownership)).
- Open questions that change scope or user-visible behaviour block approval; everything else is recorded as an assumption and repeated in the PR body.

## Template

````markdown
# <TICKET> — <title>

Ticket: <link>
Status: draft | awaiting approval | approved <date>

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

---
name: plan-review
description: Reviews the architect's plan before any code is written — by a different model family than the one that wrote it — and loops it back until the plan is sound. Replaces the human approval gate.
---

# Plan review (pre-code)

The gate between the plan and the first line of product code — every later role trusts this file. Read by a **different model family** than wrote the plan, for the same reason code review is ([reviewer › Model](../agents/reviewer.md)).

**Kind** procedure · **Used by** [reviewer](../agents/reviewer.md) · **When** the architect has written the plan (develop-flow step 2) · **Ends with** an `Approve` verdict on the plan file, or a loop back to the architect

Read-only: never edits the plan, never writes product code. The architect owns the rewrite. Set `WS` first ([AGENTS.md › Workspace paths](../../AGENTS.md#workspace-paths)).

## 1. Inputs

- `$WS/llm/scratchpad/plans/<TICKET>.md` — the plan, written to [plan-template.md](plan-template.md).
- **The whole ticket, every surface** ([AGENTS.md › Tracker](../../AGENTS.md#tracker)) — the plan is checked against the ticket, never against the plan's own summary of it.
- The code the plan touches — a plan pinned to a symbol that moved is wrong before dev starts ([AGENTS.md › Code search](../../AGENTS.md#code-search)).
- `ls $WS/llm/memory/*.md` — an entry can invalidate a plan outright ([memory](../memory/README.md)).

<a id="ticket-surfaces"></a>
### Every surface of the ticket is a requirement source

The description is one of five, and rarely the complete one. Collect all of them before judging coverage — read, comment-list, and attachment-download commands are in [AGENTS.md › Tracker](../../AGENTS.md#tracker):

| Surface | What it carries |
| --- | --- |
| **Description** | the nominal requirement, usually the oldest and stalest text on the ticket |
| **Comments** | the corrections: scope added or dropped, a decision reversed, an edge case named. Read in order, newest last — the latest word wins |
| **Attachments and screenshots** | the real acceptance criteria for UI work. Download and **look at** them: copy, states, error text, empty state, layout. A screenshot is a spec |
| **Links** | design files, related tickets, prior PRs, docs. Follow each — a linked ticket may already have moved this plan's boundary |
| **Ticket fields** | labels, type, target release, linked issues — they carry scope the prose does not repeat |

Anything found here and unanswered by the plan is a **Blocker** under check 1. Anything unreachable — dead link, attachment behind another system, screenshot that won't download — is named in the report as unread, never silently skipped.

<a id="runner"></a>
### Running this pass in Codex

Preferred, because the plan is normally written by Claude:

```bash
cat "$WS/AGENTS.md" \
    "$WS/llm/agents/reviewer.md" \
    "$WS/llm/skills/plan-review.md" \
    "$WS/llm/scratchpad/plans/<TICKET>.md" \
  | codex exec -m gpt-5.6-sol -c model_reasoning_effort="high" -
```

Model and effort come from [reviewer](../agents/reviewer.md). The output must still land in the file named under [Output](#output) — the flow gates on that file, not on a terminal transcript.

## 2. Checks

Seven, every pass:

1. **Ticket coverage** — every requirement from **every surface** appears in the plan ([above](#ticket-surfaces)), and nothing the ticket did not ask for; scope creep is a Blocker here, where removing it is free. A requirement living only in a comment or a screenshot is what this check exists to catch.
2. **Testable requirements** — each is numbered, concrete, and provable. "Improve X" is not a requirement.
3. **Grounded in the code** — files, symbols, and layers named in the plan exist and are where the plan says. Verify a sample of them; a plan that cites a moved symbol fails.
4. **Repo split and ownership** — every work item lands in a repo some role owns ([AGENTS.md › Ownership](../../AGENTS.md#ownership)), in [dependency order](../../AGENTS.md#dependency-order), with parallel-vs-sequential stated. **Lanes are per repository** ([develop-flow › Lanes](develop-flow.md#lanes)): a plan that puts two roles in one repo must mark them sequential on one branch, and a plan claiming a second branch or PR for the same repo is a Blocker.
5. **Contracts** — every cross-repo boundary has an exact pinned shape (endpoint, method, fields, types, errors) or the repos are marked sequential. A vague contract is what makes parallel dev diverge. Work inside a single repo needs no pinned contract — it needs an order.
6. **Test plan** — every requirement has a unit test or a named QA path; anything the stack cannot exercise is called out and covered by unit tests instead ([AGENTS.md › Stack limits](../../AGENTS.md#stack-limits)).
7. **Risks and assumptions** — each open question is marked blocking or assumed, and every assumption is one a reviewer would make too.

Judge the plan, not its prose. Never rewrite it or add design — a better idea is a finding with a reason, and the architect decides.

<a id="lenses"></a>
### Two lenses, run concurrently

The plan is small and the pass cheap: run it twice at once with the checks split, and merge findings before handing them back:

| Lens | Checks | Reads |
| --- | --- | --- |
| **Requirements** | 1, 2, 7 | the ticket and all its surfaces — is anything the ticket asked for missing, untestable, or assumed without saying so |
| **Feasibility** | 3, 4, 5, 6 | the code — do the named symbols exist, does the split match ownership, is the contract pinned tightly enough for two lanes to code against it, does every requirement have a test |

Give them different starting material — the requirements lens needs no code index, the feasibility lens no attachments. Merge by union (a Blocker from either is a Blocker) and hand the architect one list.

One lens is acceptable when the plan touches a single repo and has no cross-repo contract.

## 3. Loop

Blockers and Majors go back to the [architect](../agents/architect.md), which rewrites the plan file in place. Re-review the rewritten plan.

**Cap: 3 cycles.** Third pass still holding Blockers or Majors → stop and report — the plan is the cheapest place to stop and the most expensive to be wrong in.

<a id="human"></a>
## 4. When the human is asked

This gate replaces the standing human approval, not the human. Escalate — and stop — when:

- an open question changes **scope or user-visible behaviour** and no assumption is safe;
- the plan needs a repo no role owns, or one the workspace marks out of scope;
- the ticket itself is ambiguous about what "done" means;
- the cap in step 3 is hit.

Everything else is decided here. Do not ask the human to confirm a plan that passes all seven checks.

On `Approve`, **if the profile declares an in-progress transition** ([AGENTS.md › Tracker](../../AGENTS.md#tracker) · [tracker › Transitions](tracker.md#transitions)), run it here — this is the flow's only chance, and release's transition is invalid from the initial state. Where the profile declares no transitions, this gate writes nothing to the tracker.

<a id="output"></a>
## Output

Write to `$WS/llm/scratchpad/plans/<TICKET>-plan-review-<n>.md` (`<n>` = cycle, from 1) and return it to the orchestrator.

```markdown
- Sources read: description · comments (<count>) · attachments (<count>, viewed) · links (<count>, followed) · fields — <anything unreachable, named>
- Ticket coverage: <Pass | Fail> — <evidence, citing the surface each requirement came from>
- Testable requirements: <Pass | Fail> — <evidence>
- Grounded in the code: <Pass | Fail> — <which symbols were verified>
- Repo split and ownership: <Pass | Fail> — <evidence>
- Contracts: <Pass | Fail | N/A> — <evidence>
- Test plan: <Pass | Fail> — <evidence>
- Risks and assumptions: <Pass | Fail> — <evidence>

### Findings
- **<Blocker | Major | Nit>** `<plan section>` — <problem> · <fix>

### Verdict
<Approve | Approve with nits | Request changes> — <one sentence>
```

Nothing leaves the workspace here — this report is internal, for the architect to act on.

## Stop conditions

Stop and report when: the cap is hit; the ticket cannot be read ([tracker](tracker.md)); the plan names a repo no role owns; or the ticket needs a product decision nobody has made ([step 4](#human)).

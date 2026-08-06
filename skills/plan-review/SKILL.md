---
name: plan-review
description: Reviews the architect's plan before any code is written — by a different model family than the one that wrote it — and loops it back until the plan is sound. Replaces the human approval gate.
---

# Plan review (pre-code)

Pre-code gate. Use a **different model family** from the architect.

**Kind** procedure · **Used by** [reviewer](../../agents/reviewer.md) · **When** the architect has written the plan (develop-flow step 2) · **Ends with** an `Approve` verdict on the plan file, or a loop back to the architect

Read-only. Architect rewrites. Set `TROIKA_WORKSPACE` first.

## 1. Inputs

- `$TROIKA_SCRATCHPAD/plans/<TICKET>.md` — the plan, written to [plan-template.md](../plan-template/SKILL.md).
- **The whole ticket, every surface** ([AGENTS.md › Tracker](../../../AGENTS.md#tracker)) — the plan is checked against the ticket, never against the plan's own summary of it.
- The code the plan touches — a plan pinned to a symbol that moved is wrong before dev starts ([AGENTS.md › Code search](../../../AGENTS.md#code-search)).
- `ls $TROIKA_MEMORY/*.md` — an entry can invalidate a plan outright ([memory](../memory/SKILL.md)).

<a id="ticket-surfaces"></a>
### Every ticket surface

Collect all before review ([tracker](../../../AGENTS.md#tracker)):

| Surface | What it carries |
| --- | --- |
| **Description** | nominal requirement |
| **Comments** | ordered corrections; newest wins |
| **Attachments/screenshots** | download and **look at** them — copy, states, error text, empty state, layout. A screenshot is a spec |
| **Links** | designs, tickets, PRs, docs; follow all |
| **Fields** | labels, type, release, linked issues |

A requirement on any surface but absent from the plan is a **Blocker** under check 1. Name every source you could not reach as unread; never skip one silently.

<a id="runner"></a>
### Running this pass in Codex

Preferred, because the plan is normally written by Claude:

```bash
cat "$TROIKA_PROFILE" \
    "$TROIKA_HOME/agents/reviewer.md" \
    "$TROIKA_HOME/skills/plan-review.md" \
    "$TROIKA_SCRATCHPAD/plans/<TICKET>.md" \
  | codex exec -m gpt-5.6-sol -c model_reasoning_effort="high" -
```

Use [reviewer](../../agents/reviewer.md) model/effort. The gate reads the [output file](#output), not terminal text.

## 2. Checks

Every pass:

1. **Coverage:** every source requirement, no scope creep.
2. **Testability:** numbered, concrete, provable requirements.
3. **Code grounding:** named files, symbols, layers exist; sample them.
4. **Ownership:** owned repos, dependency order, explicit sequencing. One lane/branch/PR per repo.
5. **Contracts:** exact cross-repo endpoint, method, fields, types, errors — or sequential repos.
6. **Tests:** unit or QA proof per requirement; unit coverage for stack limits.
7. **Risk:** every question blocking or safely assumed.

Judge; never rewrite. Better design becomes a reasoned finding.

<a id="lenses"></a>
### Two lenses, run concurrently

Run both concurrently; merge findings:

| Lens | Checks | Reads |
| --- | --- | --- |
| **Requirements** | 1, 2, 7 | the ticket and all its surfaces — is anything the ticket asked for missing, untestable, or assumed without saying so |
| **Feasibility** | 3, 4, 5, 6 | the code — do the named symbols exist, does the split match ownership, is the contract pinned tightly enough for two lanes to code against it, does every requirement have a test |

Union verdicts. One lens is allowed for one repo with no cross-repo contract.

## 3. Loop

Blocker/Major → architect rewrites in place; re-review. Cap at 3 cycles.

<a id="human"></a>
## 4. When the human is asked

Stop and ask for:

- an open question changes **scope or user-visible behaviour** and no assumption is safe;
- the plan needs a repo no role owns, or one the workspace marks out of scope;
- the ticket itself is ambiguous about what "done" means;
- the cap in step 3 is hit.

Decide everything else here. Do not seek ceremonial approval.

On `Approve`, **if the profile declares an in-progress transition** ([AGENTS.md › Tracker](../../../AGENTS.md#tracker) · [tracker › Transitions](../tracker/SKILL.md#transitions)), run it here — this is the flow's only chance, and release's transition is invalid from the initial state. Where the profile declares no transitions, this gate writes nothing to the tracker.

<a id="output"></a>
## Output

Write to `$TROIKA_SCRATCHPAD/plans/<TICKET>-plan-review-<n>.md` (`<n>` = cycle, from 1) and return it to the orchestrator.

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

Internal only.

## Stop conditions

Stop and report when: the cap is hit; the ticket cannot be read ([tracker](../tracker/SKILL.md)); the plan names a repo no role owns; or the ticket needs a product decision nobody has made ([step 4](#human)).

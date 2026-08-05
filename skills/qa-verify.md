---
name: qa-verify
description: Verifies a change on the real local stack pointed at the dev worktrees, captures a proof per user-visible requirement, and reports a Pass/Fail verdict.
---

# QA verify (local stack)

Verifies the change on the real stack and produces the proofs the PR and the ticket carry.

**Kind** procedure · **Used by** [qa](../agents/qa.md) · **When** internal review passes, before release (develop-flow step 5) · **Ends with** a QA report file, proofs on disk, and a `Pass`/`Fail` verdict

Never edits product code. Test-data scripts go in `$WS/llm/scratchpad/`. Every stack command, port, and reset in this skill comes from [AGENTS.md › Local stack](../../AGENTS.md#stack).

## 1. Point the stack at the worktrees

The stack takes a path override per repo, so it runs the dev roles' worktrees directly. This is the **only** supported mechanism: never check a dev branch out in a primary clone (it breaks one-branch-per-worktree — [worktree](worktree.md) — and collides with whatever else uses that clone), and never edit the stack's own config to point it somewhere.

Take the override names and syntax from [AGENTS.md › Local stack](../../AGENTS.md#stack); take the worktree paths from each dev role's work log. Omit the repos the ticket doesn't touch — they default to the primary clones. A path that doesn't exist does **not** fall back to the default; the process dies at boot ([worktree › naming](worktree.md#naming)).

A worktree needs its dependencies linked before the stack can run it; the dev role has already done this, so check the link exists rather than installing.

Record the exact command line in the report — it is the definition of what was tested.

## 2. Bring the stack up

Run the profile's boot sequence, then gate on all four before verifying anything:

1. dependency/service check passes,
2. every process is running,
3. no traceback in the logs at boot,
4. the health check returns its expected status.

If the profile documents narrower ways to run the code (single services, a container fallback), say in the report which route you used — a narrower route usually ignores the worktree overrides and therefore tests the primary clone.

## 3. Verify each requirement

Walk `$WS/llm/scratchpad/plans/<TICKET>.md` requirement by requirement, on the running stack:

- **UI** — the click path from the plan's test plan, in the running app.
- **API** — call the endpoint with the documented auth; check status, body shape, and error cases against the pinned contract.
- **Async** — trigger the task, watch the logs for it, then confirm the state effect in the datastore.
- **Regression** — the same screen's other actions and the same endpoint's other cases.

Record for each: steps, request/response or screenshot, pass/fail.

## 4. Integration suite

Run it when the workspace has one covering the touched services ([AGENTS.md › Local stack](../../AGENTS.md#stack)).

**Read what its result means before reporting it.** An integration suite that builds from its own checkouts of the default branch says the default branch is healthy — nothing about your branch. Report it as a regression check, never as evidence for the change, and list every requirement it did not cover under **Not verified**.

## 5. Stack limits — what cannot be verified here

[AGENTS.md › Stack limits](../../AGENTS.md#stack-limits) lists what a green run does not prove in this workspace. State each applicable one explicitly in the report rather than letting a `Pass` imply coverage, and name what covers it instead (usually unit tests, or a consumer PR after a release tag exists).

## 6. Proofs

One artifact per user-visible requirement in `$WS/llm/scratchpad/proofs/<TICKET>/`, named after the requirement (`req-2-portfolio-filter.gif`):

- UI work: a GIF of the flow — use the tool's browser GIF recorder if it has one (capture a few frames before and after each action so playback is smooth), otherwise before/after screenshots.
- API-only work: the request and its response as a fenced transcript in the report.
- Async work: the triggering call plus the decisive log line and the resulting record.

Never fabricate a proof. If something couldn't be exercised, put it under **Not verified**.

## 7. Clean up

Take the stack down with the profile's command, then **verify nothing from a worktree survived it**. Teardown patterns are usually anchored to the primary clones, so a background worker launched from a worktree override can outlive them and run the previous branch's code in the next cycle:

```bash
pgrep -fl "$WS/llm/worktrees" || echo "no worktree processes left"
```

Kill what is left explicitly ([AGENTS.md › Local stack](../../AGENTS.md#stack)). Nothing else to undo — the path overrides live in the command line, not in any file. Leave the stack running only if the human asked; state which in the report.

## Output

Write the report to `$WS/llm/scratchpad/plans/<TICKET>-qa-<n>.md` (`<n>` = QA cycle, from 1) **and** return it to the orchestrator — [releaser](../agents/releaser.md) runs in a separate context and gates on that file ([handoff contract](../agents/README.md#handoff)).

Use the [QA report format](../agents/qa.md#output) and include: the exact command that started the stack, the branches under test, every requirement's result, the **Not verified** list from step 5, and each defect with its repro.

## Stop conditions

- Stack won't come up after the profile's documented reset and one restart → stop and report; don't debug the environment for hours.
- `Fail` on any Blocker or Major sends the work back to the owning dev role; after the fix, internal review runs again, then this skill, writing `-qa-<n+1>.md`. **Cap at 3 QA cycles**, then stop and report to the human.
- A worktree named in a work log is missing → stop and report ([worktree › Gotchas](worktree.md#gotchas)).

---
name: qa-verify
description: Verifies a change on the real local stack — browser E2E with before/after GIFs for frontend work, API calls plus datastore checks for backend work — and returns proofs and a Pass/Fail verdict.
---

# QA verify (local stack)

Verifies the change on the real stack and produces the proofs the PR and the ticket carry.

**Kind** procedure · **Used by** [qa](../agents/qa.md) · **When** every lane has cleared review and its tests (develop-flow step 6); the stack boot starts earlier, in parallel with step 3 · **Ends with** a QA report file, a proof per user-visible requirement on disk, and a `Pass`/`Fail` verdict

Never edits product code. Test-data scripts go in `$WS/llm/scratchpad/`. Every stack command, port, and reset comes from [AGENTS.md › Local stack](../../AGENTS.md#stack).

<a id="prewarm"></a>
## 0. Pre-warm — start this the moment the first dev lane reports done

Boot and seeding cost minutes, depend on the checkout rather than any verdict, and block nothing. Run them **in parallel with steps 3–5**:

- Boot from the worktree of the first lane that finishes ([step 1](#1-point-the-stack-at-the-branch-under-test)) and seed the accounts, orgs, and fixtures the plan's QA paths need.
- A later fix in that worktree is picked up on restart — cheaper than a cold boot per cycle.
- One repo, several roles: wait until the lane's roles are all done before pointing the stack. Separate repos: pre-warm each independently.

A pre-warmed stack failing its health check is a stack problem reported now, not at step 6 with everything waiting on it.

## 1. Point the stack at the branch under test

Use the override mechanism in [AGENTS.md › Local stack](../../AGENTS.md#stack) — path flags, or running from inside the worktree — and only that one: never check a dev branch out in a primary clone ([worktree](worktree.md)), never edit the stack's config.

Worktree paths come from the dev work logs; a missing path doesn't fall back, the process dies at boot. Dependencies and env files are already linked — check, don't install.

Record the exact command line **and the directory it ran in** — together they define what was tested.

## 2. Bring the stack up

Run the profile's boot sequence, then gate on all four: dependency check passes · every process running · no traceback in the logs · health check returns its expected status.

A narrower route (single services, container fallback) usually ignores the worktree and tests the primary clone — say so in the report if you used one.

## 3. Split the change

From the dev work logs, classify each requirement in `$WS/llm/scratchpad/plans/<TICKET>.md`:

| Change | Verify with | Proof |
| --- | --- | --- |
| user-visible UI | step 4 — browser E2E | before/after GIF |
| API, task, or data only | step 5 — API call + datastore | before/after transcript |
| both | steps 4 **and** 5 | both |

A change that touches frontend code but no user-visible behaviour is verified as backend and said so in the report.

## 4. Frontend — browser E2E, before/after GIF

Drive the running app with a browser automation tool that records GIFs (Claude in Chrome, or equivalent); fall back to before/after screenshots only if none exists. Per user-visible requirement, walk the plan's click path and record two artifacts:

- **before** — the same path on the base checkout, showing the old behaviour. Net-new screens have none: write `n/a — new` rather than faking one.
- **after** — the same path on the branch worktree, showing the requirement met.

Capture a few frames around each action so playback reads, and end on the state that proves the requirement (the loaded list, the saved toast), not the click. Watch the browser console and network log — an error there is a defect even when the screen looks right.

Batch every before, then restart onto the worktree and take every after: one restart per ticket.

## 5. Backend — API E2E + datastore

Per requirement, exercise the endpoint or task against the running stack and capture the whole round trip as a fenced transcript:

1. **Datastore before** — the query and the rows the change should affect.
2. **The call** — `curl` with the documented auth, showing status, headers that matter, and body. Real requests only; never a client library wrapper hiding the wire.
3. **Datastore after** — the same query, showing the state effect.
4. **Error cases** — bad auth, missing field, not-found — status and body shape checked against the pinned contract.

Async requirements add the decisive log line between 2 and 3 — task picked up, task completed. A success response without the row changing is a defect.

## 6. Regression and integration suite

Exercise adjacent paths — the same screen's other actions, the same endpoint's other cases — then the workspace's integration suite where one covers the touched services ([AGENTS.md › Local stack](../../AGENTS.md#stack)).

**Read what its result means before reporting it.** A suite that builds from its own checkouts of the default branch says the default branch is healthy — nothing about your branch. Report it as a regression check, never as evidence for the change.

## 7. Stack limits

[AGENTS.md › Stack limits](../../AGENTS.md#stack-limits) lists what a green run does not prove. State each applicable one rather than letting `Pass` imply coverage, and name what covers it instead (unit tests, a manual out-of-band check, a consumer PR after a release tag).

## 8. Proofs for the PR

One directory per ticket, `$WS/llm/scratchpad/proofs/<TICKET>/`, one file per requirement per side, named after the requirement:

```
req-2-portfolio-filter-before.gif
req-2-portfolio-filter-after.gif
req-3-export-endpoint.md          # backend: the step-5 transcript
```

List them by filename against their requirement number — [release-pr](release-pr.md#4-proofs) attaches them and references those names from the PR body, so a name that matches no requirement row loses the link.

**Never fabricate a proof.** Anything not exercised goes under **Not verified**, with why.

## 9. Clean up

Take the stack down with the profile's command, then verify nothing from a worktree survived — teardown is usually anchored to the primary clones, so a worktree-launched worker can outlive it and run old code next cycle:

```bash
pgrep -fl "$WS/llm/worktrees" || echo "no worktree processes left"
```

Kill what is left explicitly ([AGENTS.md › Local stack](../../AGENTS.md#stack)). Close any browser tabs the run opened. Leave the stack running only if the human asked; say which in the report.

## Output

Write the report to `$WS/llm/scratchpad/plans/<TICKET>-qa-<n>.md` (`<n>` = QA cycle, from 1) **and** return it to the orchestrator — [releaser](../agents/releaser.md) runs in a separate context and gates on that file ([handoff contract](../agents/README.md#handoff)).

Use the [QA report format](../agents/qa.md#output) and include: the exact command and directory that started the stack, the branches under test, every requirement's result with its proof filenames, the **Not verified** list, and each defect with its repro.

## Stop conditions

- Stack won't come up after the profile's documented reset and one restart → stop and report; don't debug the environment for hours.
- Browser tool unresponsive or a page failing after 2–3 attempts → stop and report; don't retry the same action or wander the app.
- `Fail` on any Blocker or Major sends the work back to the owning dev role; after the fix, internal review runs again, then this skill, writing `-qa-<n+1>.md`. **Cap at 3 QA cycles**, then stop and report to the human.
- A worktree named in a work log is missing → stop and report ([worktree › Gotchas](worktree.md#gotchas)).

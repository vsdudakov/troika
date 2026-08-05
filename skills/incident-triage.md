---
name: incident-triage
description: Investigates a production symptom from the observability platform — aggregate to the hot service, read raw events, follow traces, and land on a cause with evidence, changing nothing.
---

# Incident triage

A reported symptom becomes a located cause with the queries that prove it.

**Kind** procedure · **Used by** [architect](../agents/architect.md) · [backend-dev](../agents/backend-dev.md) · **When** a production error, alert, or "it broke for tenant X" arrives, before any plan or fix · **Ends with** a written finding — service, error, window, blast radius, evidence — and a recommendation, with nothing changed

**Read-only.** Query the observability platform, read code, nothing else: no writes to the platform, no config change, no restart, no deploy, no fix. The credentials, query shapes, and per-platform traps are in [AGENTS.md › Observability](../../AGENTS.md#observability); production access rules are in [AGENTS.md › Gotchas](../../AGENTS.md#gotchas).

## 1. Pin the question

Before the first query, write down: the symptom in one sentence, the time window, and the scope (environment, service, tenant) if known. An unbounded query over "everything, recently" is slow, rate-limited, and answers nothing.

## 2. Aggregate before reading

Count errors grouped by a facet — service first, then tenant or error kind — to find what is actually on fire. Read the counts as a shape, not a total: one stack trace or HTML error page can be dozens of lines, so a big number may be one event ([AGENTS.md › Observability](../../AGENTS.md#observability)).

## 3. Read raw events

Narrow to the hot facet and read the newest events in full — message, tenant, timestamps. This is where the actual error string comes from, and the error string is what the finding is built on. Quote it exactly; never paraphrase an error.

## 4. Follow it into the code

Take the symbol, endpoint, or task name from the event and read the code path ([AGENTS.md › Code search](../../AGENTS.md#code-search) — refresh the index first). Traces or spans, where the platform has them, connect the failing call to its caller.

The goal is one of: a specific code path that can produce exactly this error, a recent change that introduced it (check when the error first appears against when things shipped), or an external dependency failing.

## 5. Establish blast radius and first occurrence

Widen the window deliberately — once, on the narrowed query — to answer two things the humans always ask: **when did this start** and **how many tenants/requests are affected**. A cause without a start time is a guess.

## 6. Write the finding

Symptom · window queried · service and error string (verbatim) · first occurrence · blast radius · the code path or change that explains it · what is still unexplained. Include the queries themselves, so the next person can re-run them rather than rediscover them.

Recommend the next action — a fix through the normal flow, a ticket ([ticket-intake](ticket-intake.md)), or a human decision — and stop there. **Triage does not fix.**

An observation that will outlive the incident (a recurring flake, an environment trap, a platform quirk) goes to [`memory/`](../memory/README.md), dated.

## Output

The finding as above, with the queries · the recommended next action · anything checked and ruled out, so it is not re-checked.

## Stop conditions

Stop and hand back when: the platform's credentials fail (verify with a real call before blaming the query); the symptom is not visible in the window given and widening does not surface it; the cause is outside the code roles own; or acting on it would require a write, a restart, or a deploy.

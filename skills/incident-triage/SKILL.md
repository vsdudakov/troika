---
name: incident-triage
description: Investigates a production symptom from the observability platform — aggregate to the hot service, read raw events, follow traces, and land on a cause with evidence, changing nothing.
---

# Incident triage

Locate cause with reproducible evidence.

**Kind** procedure · **Used by** [architect](../../agents/architect.md) · [backend-dev](../../agents/backend-dev.md) · **When** a production error, alert, or "it broke for tenant X" arrives, before any plan or fix · **Ends with** a written finding — service, error, window, blast radius, evidence — and a recommendation, with nothing changed

Read-only: query telemetry and code. No write, config, restart, deploy, fix. Follow profile access rules.

## 1. Pin the question

Pin symptom, window, environment/service/tenant. No unbounded query.

## 2. Aggregate before reading

Count by service, then tenant/error. Read counts as a shape, not a total: one stack trace can be dozens of lines, so a big number may be one event.

## 3. Read raw events

Read newest hot events fully. Quote exact error.

## 4. Follow it into the code

Refresh index; trace event symbol/endpoint/task into code and callers.

The goal is one of: a specific code path that can produce exactly this error, a recent change that introduced it (check when the error first appears against when things shipped), or an external dependency failing.

## 5. Establish blast radius and first occurrence

Widen narrowed query once: first occurrence and affected tenants/requests.

## 6. Write the finding

Write symptom · window · service · exact error · first occurrence · blast radius · explaining path/change · unknowns · queries.

Recommend normal fix flow, ticket, or human decision. Do not fix.

An observation that will outlive the incident (a recurring flake, an environment trap, a platform quirk) goes to [`memory/`](../memory/SKILL.md), dated.

## Output

The finding as above, with the queries · the recommended next action · anything checked and ruled out, so it is not re-checked.

## Stop conditions

Stop and hand back when: the platform's credentials fail (verify with a real call before blaming the query); the symptom is not visible in the window given and widening does not surface it; the cause is outside the code roles own; or acting on it would require a write, a restart, or a deploy.

---
name: incident-triage
description: Investigates a production symptom from the observability platform — aggregate to the hot service, read raw events, follow traces, and land on a cause with evidence, changing nothing.
argument-hint: <issue link | stack trace | event>
---

Run Troika's **incident-triage** procedure for: $ARGUMENTS

1. Resolve the workspace, before anything else:

   ```bash
   eval "$(python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --ensure)"
   ```

   That exports `WS`, `TROIKA_PROFILE`, `TROIKA_HOME`, `TROIKA_SCRATCHPAD`,
   `TROIKA_WORKTREES`, and `TROIKA_MEMORY`, reading `<workspace>/.troika.json` where the
   workspace declares them, and creates the three it writes into. It exits non-zero when there is no workspace above the current
   directory — **stop there and say so**; a guessed path writes handoff files nobody reads.

2. Read the procedure: `${CLAUDE_PLUGIN_ROOT}/skills/incident-triage/SKILL.md`. If that
   variable is unset, read `$TROIKA_HOME/skills/incident-triage/SKILL.md` instead.
3. Read `$TROIKA_PROFILE` — the workspace profile. Every repo, command, branch, base ref,
   tracker, and URL comes from there; the procedure names none of them, and where the
   profile declares a limit the profile wins.
4. Follow the procedure in order. Every step is a gate: never advance past a failed one.

Roles run with their cwd inside a worktree, so every path from step 1 is used verbatim and
absolute. A relative one writes a file no later role finds.

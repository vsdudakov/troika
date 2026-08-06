---
name: qa
description: Verifies a change on the real local stack — browser E2E with before/after GIFs for frontend work, API calls plus datastore checks for backend work — and returns proofs and a Pass/Fail verdict.
argument-hint: <PR number | PR link | TICKET>
---

Run Troika's **qa-verify** procedure.

**Argument** — `<PR number | PR link | TICKET>`: $ARGUMENTS

With no argument, ask for one and stop — do not guess.

1. Resolve the workspace, before anything else:

   ```bash
   eval "$(python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --ensure)"
   ```

   That exports `WS`, `TROIKA_PROFILE`, `TROIKA_HOME`, `TROIKA_SCRATCHPAD`,
   `TROIKA_WORKTREES`, and `TROIKA_MEMORY`, reading `<workspace>/.troika.json` where the
   workspace declares them, and creating the three it writes into. It exits non-zero when
   there is no workspace above the current directory — **stop there and say so**; a guessed
   path writes handoff files nobody reads.

2. Read the procedure: `${CLAUDE_PLUGIN_ROOT}/skills/qa-verify/SKILL.md`. If that variable is
   unset — a plain clone rather than an installed plugin — read
   `$TROIKA_HOME/skills/qa-verify/SKILL.md` instead.
3. Read `$TROIKA_PROFILE` — the workspace profile. Every repo, command, branch, base ref,
   tracker, and URL comes from there; the procedure names none of them, and where the
   profile declares a limit the profile wins.
4. Follow the procedure in order. Every step is a gate: never advance past a failed one, and
   stop on any of its stop conditions rather than working around it.

Roles run with their cwd inside a worktree, so every path from step 1 is used verbatim and
absolute. A relative one writes a file no later role finds.

---
name: spike
description: Investigates a ticket read-only and produces a reviewed implementation plan — the pipeline's planning half, stopped before any code is written.
argument-hint: <TICKET>
---

Run Troika's **spike** procedure.

**Argument** — `<TICKET>`: $ARGUMENTS

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

2. Read the procedure: `${CLAUDE_PLUGIN_ROOT}/skills/spike/SKILL.md`. If that variable is
   unset — a plain clone rather than an installed plugin — read
   `$TROIKA_HOME/skills/spike/SKILL.md` instead.
3. Read `$TROIKA_PROFILE` — the workspace profile. Every repo, command, branch, base ref,
   tracker, and URL comes from there; the procedure names none of them, and where the
   profile declares a limit the profile wins.
4. Follow the procedure in order. Every step is a gate: never advance past a failed one, and
   stop on any of its stop conditions rather than working around it.

Roles run with their cwd inside a worktree, so every path from step 1 is used verbatim and
absolute. A relative one writes a file no later role finds.

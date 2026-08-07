---
name: dev
description: The full pipeline from ticket to merge-ready PR — bug tickets reproduce first, feature tickets plan first, then parallel dev, internal review loop, unit tests on the change only, QA before/after on the local stack, release, CI.
argument-hint: <TICKET>
---

Run Troika's **develop-flow** procedure.

**Argument** — `<TICKET>`: $ARGUMENTS

With no argument, ask for one and stop — do not guess.

**Flag** — `--ask`: stop at the reporter-review gate and wait for their answer. Without it the run is unattended end to end, and there is no flag for that direction because a plain run already is it.

1. Resolve the workspace, before anything else:

   ```bash
   eval "$(python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --ensure)"
   ```

   `${CLAUDE_PLUGIN_ROOT}` is Claude Code's name for the plugin's install directory. On a
   host that does not export it, substitute that directory — the one holding this plugin's
   `plugin/` and `skills/` trees — everywhere the variable appears below.

   That exports `TROIKA_WORKSPACE`, `TROIKA_PROFILE`, `TROIKA_SCRATCHPAD`,
   `TROIKA_WORKTREES`, and `TROIKA_MEMORY`, reading `<workspace>/.troika/settings.json`
   where the workspace declares them, and creating the three it writes into. It exits
   non-zero when no ancestor of the current directory holds that file — **stop there and
   say so**, and point at `/tr:setup`; a guessed path writes handoff files nobody reads.

2. Read the procedure: `${CLAUDE_PLUGIN_ROOT}/skills/develop-flow/SKILL.md`.
3. Read `$TROIKA_PROFILE` — the workspace profile. Every repo, command, branch, base ref,
   tracker, and URL comes from there; the procedure names none of them, and where the
   profile declares a limit the profile wins.
4. Follow the procedure in order. Every step is a gate: never advance past a failed one, and
   stop on any of its stop conditions rather than working around it.

Roles run with their cwd inside a worktree, so every path from step 1 is used verbatim and
absolute. A relative one writes a file no later role finds.

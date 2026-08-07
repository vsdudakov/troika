---
name: demo
description: Builds the demo integration branch — reset it from the default branch, merge the demo-labeled PRs in a conflict-minimising order, deploy, and prepare the team notification.
argument-hint: [LABEL]
---

Run Troika's **demo-prep** procedure.

**Argument** — `[LABEL]`: $ARGUMENTS

With no argument, use the profile's default and say which you used.

1. Resolve the workspace, before anything else:

   ```bash
   eval "$(python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --ensure)"
   ```

   That exports `TROIKA_WORKSPACE`, `TROIKA_PROFILE`, `TROIKA_SCRATCHPAD`,
   `TROIKA_WORKTREES`, and `TROIKA_MEMORY`, reading `<workspace>/.troika/settings.json`
   where the workspace declares them, and creating the three it writes into. It exits
   non-zero when no ancestor of the current directory holds that file — **stop there and
   say so**, and point at `/tr:setup`; a guessed path writes handoff files nobody reads.

2. Read the procedure: `${CLAUDE_PLUGIN_ROOT}/skills/demo-prep/SKILL.md`.
3. Read `$TROIKA_PROFILE` — the workspace profile. Every repo, command, branch, base ref,
   tracker, and URL comes from there; the procedure names none of them, and where the
   profile declares a limit the profile wins.
4. Follow the procedure in order. Every step is a gate: never advance past a failed one, and
   stop on any of its stop conditions rather than working around it.

Roles run with their cwd inside a worktree, so every path from step 1 is used verbatim and
absolute. A relative one writes a file no later role finds.

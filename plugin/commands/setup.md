---
name: setup
description: Creates a workspace — the .troika directory, its settings, and the profile every other procedure reads — by investigating the repos first and asking only what they cannot answer.
argument-hint: [PATH]
---

Run Troika's **workspace-setup** procedure — create a workspace.

**Argument** — `[PATH]`: $ARGUMENTS

With no argument, use the current directory, and confirm it with the caller before writing.

This is the one command that runs before a workspace exists, so it does **not** resolve one
first. It creates it.

1. Read the procedure: `${CLAUDE_PLUGIN_ROOT}/skills/workspace-setup/SKILL.md`. `${CLAUDE_PLUGIN_ROOT}`
   is Claude Code's name for the plugin's install directory; on a host that does not export
   it, substitute that directory — the one holding this plugin's `plugin/` and `skills/` trees.
2. Follow it in order. It fixes the workspace root, scaffolds `.troika/`, investigates the
   repos, asks only what they cannot answer, and writes the profile.
3. Every step is a gate: never advance past a failed one, and stop on any of its stop
   conditions rather than working around it.

Where a workspace already exists — `.troika/settings.json` or the profile is present — **say so
and ask** what to do: leave it, update it against what the repos now say, or rewrite the
profile from the template. Default to leaving it, and never overwrite what a human wrote
without being asked to in words.

Every other `/tr:*` command resolves that workspace instead of creating one.

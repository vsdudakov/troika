# plugin/

What turns this repo into a plugin for Claude Code, Codex, and Cursor. Three manifests, one
generated command per procedure, and the resolver every role runs first.

- [`../.claude-plugin/`](../.claude-plugin/plugin.json) — Claude Code: commands, skills, and
  the eight roles as subagents. [`marketplace.json`](../.claude-plugin/marketplace.json)
  beside it makes the repo its own single-plugin marketplace.
- [`../.codex-plugin/plugin.json`](../.codex-plugin/plugin.json) — Codex: skills only, the
  one component type its manifest accepts. Its marketplace is
  [`../.agents/plugins/marketplace.json`](../.agents/plugins/marketplace.json).
- [`../.cursor-plugin/plugin.json`](../.cursor-plugin/plugin.json) — Cursor: commands as a
  glob, plus the same skills.
- `commands/<name>.md` — **generated**, one per procedure, by
  [`generate.py`](generate.py). `/troika:<name>` in Claude Code and Cursor.
- [`resolve.py`](resolve.py) — where this workspace keeps its files. Every command runs it
  first.

The skills themselves are not here. `../skills/<name>/SKILL.md` is the procedure *and* the
skill: all three hosts discover a skill as a directory holding that file, so there is no
wrapper and nothing to keep in sync. Only the commands are generated, because a command is
the one thing a `SKILL.md` cannot be — an entry in the `/` menu, with an argument hint, that
resolves the workspace before the procedure starts.

```bash
python3 plugin/generate.py          # rewrite the commands after editing a procedure
python3 plugin/generate.py --check  # what tests/check.py runs
```

Never hand-edit a command: edit the procedure's frontmatter and regenerate. `check.py` fails
on a stale command, and on one left behind by a deleted procedure — an orphan still appears
in the `/` menu and sends the model to read a file that is gone.

## The two roots

A plugin installs into the host's **cache**, not into the workspace. The cached copy holds
the roles and the procedures; it cannot hold `AGENTS.md`, `worktrees/`, `scratchpad/`, or
`memory/`, which are per-workspace and differ for every organisation the tree is dropped
into. So a command reads its procedure from the plugin root, and resolves everything it
writes through the workspace:

```bash
eval "$(python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py")"
```

That prints — and `eval` exports — six paths:

| Variable | Default | Holds |
| --- | --- | --- |
| `WS` | the directory found | the workspace root; repos are `$WS/<repo>` |
| `TROIKA_PROFILE` | `$WS/AGENTS.md` | the project profile |
| `TROIKA_HOME` | `$WS/troika` | this tree, when it is cloned rather than installed |
| `TROIKA_WORKTREES` | `$WS/troika/worktrees` | one checkout per branch |
| `TROIKA_SCRATCHPAD` | `$WS/troika/scratchpad` | plans, reviews, work logs, proofs |
| `TROIKA_MEMORY` | `$WS/troika/memory` | dated observations about this workspace |

No role spells any of these out — `check.py` fails a file that hardcodes one — because the
workspace is allowed to move them.

## Configuring a workspace

`.troika.json` at the workspace root is the one place a path is declared. Every key is
optional and relative to the file, and an absolute value is taken as-is, so state can live
anywhere:

```json
{
  "profile": "AGENTS.md",
  "home": "troika",
  "scratchpad": "/Volumes/fast/acme/scratchpad",
  "worktrees": "/Volumes/fast/acme/worktrees",
  "memory": "troika/memory"
}
```

Put one in each folder that holds a set of repos — one per organisation, per client, per
checkout — and the same installed plugin serves all of them. The resolver walks up from
wherever the role is standing, so a role deep inside a worktree finds the workspace that
owns it, not the one you happened to install from.

With no `.troika.json` anywhere, the resolver falls back to the nearest ancestor holding
both `AGENTS.md` and a `troika/` directory, with the default layout above — a plain clone
keeps working. It requires *both*, because repos carry their own `AGENTS.md` and stopping at
the first one found would resolve a worktree as the workspace and scatter handoff files
through it.

A non-zero exit means no workspace was found. That is a stop, not a default: a guessed path
writes proofs nobody reads.

## Install

**Claude Code**

```bash
claude plugin marketplace add vsdudakov/troika      # or an absolute path to a local clone
claude plugin install troika@troika                 # --scope project to pin it to one workspace
```

Committed per workspace instead, in `<workspace>/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "troika": { "source": { "source": "github", "repo": "vsdudakov/troika" } }
  },
  "enabledPlugins": { "troika@troika": true }
}
```

**Codex**

```bash
codex plugin marketplace add <absolute path to this clone>
codex plugin add troika
```

Codex installs are global — there is no per-project enable, and no `commands` concept
either, so its surface is the skills.

**Cursor** reads `.cursor-plugin/plugin.json` from the same clone.

Validate a change to any manifest against Codex's own checker before pushing:

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

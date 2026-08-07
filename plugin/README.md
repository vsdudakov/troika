# plugin/

What turns this repo into a plugin for Claude Code, Codex, and Cursor. Three manifests, a
generated command per entry-point procedure, and the resolver every role runs first.

- [`../.claude-plugin/`](../.claude-plugin/plugin.json) — Claude Code: commands, skills, and
  the eight roles as subagents. [`marketplace.json`](../.claude-plugin/marketplace.json)
  beside it makes the repo its own single-plugin marketplace.
- [`../.codex-plugin/plugin.json`](../.codex-plugin/plugin.json) — Codex: skills only, the
  one component type its manifest accepts. Its marketplace is
  [`../.agents/plugins/marketplace.json`](../.agents/plugins/marketplace.json).
- [`../.cursor-plugin/plugin.json`](../.cursor-plugin/plugin.json) — Cursor: commands as a
  glob, plus the same skills.
- `commands/<alias>.md` — **generated** by [`generate.py`](generate.py) from its `COMMANDS`
  map: `setup`, `dev`, `spike`, `fix`, `review`, `qa`, `triage`, `release`, `demo` — plus
  `help`, generated from the same map, which lists them all in the session.
  `/tr:<alias>` in Claude Code and Cursor. A procedure absent from that map has no command
  and stays a skill — the steps the flow runs for you are wrong to start on their own.
- [`resolve.py`](resolve.py) — where this workspace keeps its files. Every command runs it
  first, except `setup`, which is the command that creates the workspace it would resolve.

The skills themselves are not here. `../skills/<name>/SKILL.md` is the procedure *and* the
skill: all three hosts discover a skill as a directory holding that file, so there is no
wrapper and nothing to keep in sync. Only the commands are generated, because a command is
the one thing a `SKILL.md` cannot be — an entry in the `/` menu, with an argument hint, that
resolves the workspace before the procedure starts.

```bash
python3 plugin/generate.py          # rewrite the commands after editing a procedure
python3 plugin/generate.py --check  # what tests/check.py runs
```

Never hand-edit a command: edit the procedure's frontmatter (or `COMMANDS`) and regenerate.
`check.py` fails on a stale command, and on one left behind by a deleted procedure or one
dropped from the map — an orphan still appears in the `/` menu and sends the model to read a
file that may be gone.

## The two roots

A plugin installs into the host's **cache**, not into the workspace. The cached copy holds
the roles and the procedures; it cannot hold the profile, the worktrees, the scratchpad or
the memory, which are per-workspace and differ for every organisation the tree is dropped
into. So a command reads its procedure from the plugin root, and resolves everything it
writes through the workspace:

```bash
eval "$(python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py")"
```

That prints — and `eval` exports — five paths:

| Variable | Default | Holds |
| --- | --- | --- |
| `TROIKA_WORKSPACE` | the directory found | the workspace root; repos are `$TROIKA_WORKSPACE/<repo>` |
| `TROIKA_PROFILE` | `.troika/PROFILE.md` | the project profile |
| `TROIKA_WORKTREES` | `.troika/worktrees` | one checkout per branch |
| `TROIKA_SCRATCHPAD` | `.troika/scratchpad` | plans, reviews, work logs, proofs |
| `TROIKA_MEMORY` | `.troika/memory` | dated observations about this workspace |

No role spells any of these out — `check.py` fails a file that hardcodes one — because the
workspace is allowed to move them.

## Configuring a workspace

`/tr:setup` creates the workspace. It writes `.troika/settings.json`, the one place a
path is declared, plus a `.gitignore` and the three state directories, and then fills in the
profile from what the repos say:

```
<workspace>/
├── .troika/
│   ├── settings.json   the paths — committed
│   ├── PROFILE.md      the profile every role reads — committed
│   ├── .gitignore      keeps the three below out of the workspace's history
│   ├── scratchpad/     plans, reviews, work logs, proofs
│   ├── worktrees/      one checkout per branch
│   └── memory/         dated observations
├── repo-a/
└── repo-b/
```

Every settings key is optional and relative to the workspace, and an absolute value is taken
as-is, so state can live anywhere:

```json
{
  "profile": ".troika/PROFILE.md",
  "scratchpad": "/Volumes/fast/acme/scratchpad",
  "worktrees": "/Volumes/fast/acme/worktrees",
  "memory": ".troika/memory"
}
```

Run setup in each folder that holds a set of repos — one per organisation, per client, per
checkout — and the same installed plugin serves all of them. The resolver walks up from
wherever the role is standing, so a role deep inside a worktree finds the workspace that
owns it, not the one you happened to install from.

`.troika/settings.json` is the **only** marker. Nothing falls back: a folder without one is a
folder nobody has run setup in, and the resolver exits non-zero saying so. That is a stop,
not a default — a guessed path writes proofs nobody reads, and a walk that accepted a repo's
own `AGENTS.md` would resolve a worktree as the workspace.

Scaffold without a model, if you prefer — `<plugin root>` is where the host installed it:

```bash
python3 <plugin root>/plugin/resolve.py --init <workspace>   # settings, .gitignore, state dirs
```

That leaves the profile to write by hand from [`PROFILE.template.md`](../PROFILE.template.md);
`/tr:setup` is the same job with the repos read for you.

## Install

**Claude Code**

```bash
claude plugin marketplace add vsdudakov/troika
claude plugin install tr@troika                 # --scope project to pin it to one workspace
```

Then restart the host and run `/tr:setup` in the folder that holds your repos. Nothing
else works until that has been done once.

Committed per workspace instead, in `<workspace>/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "troika": { "source": { "source": "github", "repo": "vsdudakov/troika" } }
  },
  "enabledPlugins": { "tr@troika": true }
}
```

**Codex**

```bash
codex plugin marketplace add vsdudakov/troika
codex plugin add tr
```

Codex installs are global — there is no per-project enable, and no `commands` concept
either, so its surface is the skills.

**Cursor** reads `.cursor-plugin/plugin.json` from the same marketplace.

Validate a change to any manifest against Codex's own checker before pushing:

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

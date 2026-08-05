# llm/

A tool-neutral agent harness: roles, procedures, templates. Plain markdown, so Claude Code, Cursor, and Codex all load it by path; the YAML frontmatter (`name`, `description`) is the one convention all three read.

**Organisation-neutral.** Nothing here names a repo, a command, a tracker, a URL, or a person. Every such fact comes from the workspace's [`../AGENTS.md`](../AGENTS.md) — the *project profile* — which each organisation writes once from [AGENTS.template.md](AGENTS.template.md). Drop this tree into another workspace, write that one file, and the pipeline runs unchanged.

That cuts both ways: where the profile declares a *limit* — no ticket transitions, one repo and one PR, no build step, a base branch that is not `origin/main` — the roles follow the profile, not the generic wording. A skill that hardcodes any of those is a bug in this tree.

```
<workspace>/
  AGENTS.md        the project profile — org-specific, lives with the org's workspace
  llm/             this repo — generic, shared across orgs
  <repos…>         the product repos, each an independent clone
```

- [`agents/`](agents/README.md) — the roles: architect, backend-dev, frontend-dev, reviewer, tester, qa, releaser, commenter. Who acts, what gates them, which model and effort each runs on.
- [`skills/`](skills/README.md) — the procedures, references, and templates. The pipeline is [develop-flow](skills/develop-flow.md).
- [`memory/`](memory/README.md) — dated, provisional observations about the workspace it is cloned into. **Gitignored** — memory is per-workspace, not shared.
- [`worktrees/`](worktrees/README.md) — the per-branch checkouts. **Gitignored**, and not configuration: never recurse into it when loading this tree.
- [`scratchpad/`](scratchpad/README.md) — role handoff files. **Gitignored**, not configuration either.

## Set up in a new workspace

1. Clone this repo into the workspace root as `llm/`.
2. Copy [AGENTS.template.md](AGENTS.template.md) to `<workspace>/AGENTS.md` and fill every section. The **anchors are a contract** — roles and skills link to them by name, and a missing one is a role reading a dead link.
3. Run the pipeline: `run llm/skills/develop-flow.md for <TICKET>`. Run one role: `read llm/agents/qa.md and verify <TICKET> on the local stack`.

Everything under `memory/`, `scratchpad/`, and `worktrees/` is per-workspace and ignored; each keeps a tracked `README.md` so the folder itself survives a clone. Because they are *ignored* rather than absent, `git clean -xfd` in this repo deletes all three — in-flight branches included. Clean with explicit paths or not at all.

## Conventions

Roles run in separate contexts and hand off through files, never shared memory — the [handoff contract](agents/README.md#handoff).

**Absolute paths.** Every role's cwd is inside a worktree, so `llm/scratchpad/` is not below it. Set `WS` once per session ([AGENTS.md › Workspace paths](../AGENTS.md#workspace-paths)) and use it verbatim; a relative path writes a file no later role finds.

<a id="shell-quoting"></a>
**Posting text through a shell.** Findings and PR bodies contain backticks, `$`, and quotes; inside `"…"` the shell executes backticks as command substitutions and silently drops the result. Always pass generated text through a quoted heredoc, never a double-quoted argument:

```bash
gh pr comment 42 --body "$(cat <<'EOF'
- **Major** `service/portfolio.py:88` — N+1 · use `select_related`
EOF
)"
```

The same applies to `gh pr create --body`, any tracker CLI's comment command, and `git commit -m`.

## File shape

Every file in `agents/` and `skills/` opens with:

```markdown
---
name: <slug matching the filename>
description: <one line — what it is; tools use it to pick the file>
---
```

**Agents** then carry a three-item header list — `- **Owns**` / `- **Runs**` + `**Step**` / `- **Model**` — where `**Model**` nests one sub-bullet per line: `**Claude**` · `**Codex**` · `**Why**` · optional `**Raise it when**` / `**Drop it when**`. Then the same five sections, in this order: `Scope` · `Inputs` · `Rules` · `Gates` · `Output`. The list markers matter: three bare lines collapse into one paragraph in every markdown renderer.

**Skills** carry a one-line header with the same four fields — `**Kind**` · `**Used by**` · `**When**` · `**Ends with**` — and follow their kind's body shape:

| Kind | Body |
| --- | --- |
| procedure | numbered `## 1.` … steps, each a gate, then `## Output` and `## Stop conditions` |
| reference | topic sections, then `## Gotchas` |
| template | `## Fill rules`, then `## Template` |

# AGENTS.template.md

The project profile every workspace must provide. Copy to `<workspace>/AGENTS.md`, fill it in, delete the guidance in angle brackets.

The harness in `llm/` is organisation-neutral: roles and skills link into this file **by anchor**. Keep the anchor ids below exactly as written — the headings above them are yours to reword. An anchor with no content is a role reading a dead link.

| Anchor | Must answer | Read by |
| --- | --- | --- |
| `#rules` | the rules that bind every session, with or without a role | everyone |
| `#comments` | when a comment is allowed in code | dev roles, reviewer |
| `#no-ai-attribution` | what may never appear in commits, PRs, tracker text | everyone |
| `#voice` | how outward-facing text sounds | commenter |
| `#repo-map` | which repos exist, what each is, what is out of scope | everyone |
| `#ownership` | which role owns which repo or app | everyone |
| `#workspace-paths` | the workspace root and the absolute-path rule | everyone |
| `#code-search` | the code search tool and how to refresh its index | architect, dev roles, reviewer |
| `#branches` | default branch, branch naming, worktree dependency setup, push quirks | dev roles, releaser |
| `#dependency-order` | provider → consumer order across repos, and how shared libraries are released | architect, releaser |
| `#commands` | per repo: targeted tests, full lint, full suite, migrations | dev roles, reviewer |
| `#style` | per-language style rules | dev roles, reviewer |
| `#layering` | the architectural layers, if the codebase has them | backend-dev, reviewer |
| `#tests` | test framework, naming, location, coverage gate | dev roles, reviewer |
| `#stack` | how to run the product locally and point it at a worktree | qa |
| `#stack-limits` | what the local stack cannot verify | qa, architect |
| `#tracker` | tracker URL, project key, CLI, auth check, transition names | architect, releaser |
| `#pull-requests` | PR host, title format, CI watch, review-bot loop | releaser |
| `#pr-template` | the PR body the team uses | releaser, commenter |
| `#gotchas` | destructive commands and traps specific to this workspace | everyone |

## Skeleton

```markdown
# AGENTS.md — <Org>

The project profile for the harness in llm/. Roles reference these sections by anchor.

<a id="rules"></a>
## Rules
- No secrets in code.
<a id="comments"></a>
- Comments only for a non-obvious why.
<a id="no-ai-attribution"></a>
- No AI attribution anywhere.
- <ask-before-committing, signing, branch policy>

<a id="repo-map"></a>
## Repo map
<one line per repo: what it is, its stack, what is out of scope>

<a id="ownership"></a>
## Ownership
<role → repos table>

<a id="workspace-paths"></a>
## Workspace paths
<workspace root; llm/worktrees/ and llm/scratchpad/ are anchored to it; set WS once>

<a id="code-search"></a>
## Code search
<tool, refresh command, why a stale index is wrong>

<a id="branches"></a>
## Branches
<default branch, naming, worktree dependency wiring, push quirks>

<a id="dependency-order"></a>
## Dependency order
<providers before consumers; how a shared library is versioned and released>

<a id="commands"></a>
## Commands
<per-repo table: targeted tests | lint; plus full suite, migrations, formatter traps>

<a id="style"></a>
## Style
<per language; import rules>
<a id="layering"></a>
<layering gate, if any>

<a id="tests"></a>
## Tests
<framework, naming, location, coverage gate, mocking policy>

<a id="stack"></a>
## Local stack
<how to run everything, how to point it at a worktree, ports, health check, teardown>
<a id="stack-limits"></a>
### Stack limits
<what a green run does not prove>

<a id="tracker"></a>
## Tracker
<URL, project key, CLI, auth verification, workflow transitions, attachments>

<a id="pull-requests"></a>
## Pull requests
<host, title format, CI watch command, review-bot loop>
<a id="pr-template"></a>
### PR body
<the template>

<a id="voice"></a>
## Voice
<who the text sounds like, with do/don't examples>

<a id="gotchas"></a>
## Gotchas
<destructive commands, masked failures, environment traps>
```

## Rules for writing it

- **One home per fact.** If it is here, no role file repeats it — roles link.
- Commands are copy-pasteable, with the environment variables they need.
- Name what a green result does *not* prove; that is the section roles get wrong most.
- If the organisation has no equivalent of a section (no layering, no local stack), keep the anchor and say so in one line. A missing anchor breaks links; an honest "not applicable" does not.

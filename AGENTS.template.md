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
| `#code-search` | the code search tool and how to refresh its index | architect, dev roles, reviewer, tester |
| `#branches` | **remote name and default branch (the base ref every diff and worktree uses)**, branch naming, worktree dependency setup, push quirks | dev roles, reviewer, tester, releaser |
| `#dependency-order` | provider → consumer order across repos, and how shared libraries are released | architect, releaser |
| `#commands` | per repo or area: narrowed tests, **the exact verification commands a dev role must run as its gate** (lint, and a type check or build only if that is how this workspace runs it), full suite, per-runner parallel flags; and for migrations, **the generator command plus what may be done to a revision that has already been applied** | dev roles, reviewer, tester |
| `#style` | per-language style rules | dev roles, reviewer |
| `#layering` | the architectural layers, if the codebase has them | backend-dev, reviewer |
| `#tests` | test framework, naming, location, coverage gate, who runs them and when | dev roles, reviewer, tester |
| `#stack` | how to run the product locally and point it at a worktree | qa |
| `#stack-limits` | what the local stack cannot verify | qa, architect |
| `#tracker` | tracker URL, project key, CLI or API, auth check, **which writes a role may make — transition names, or an explicit "there are none" plus the equivalent write** | architect, releaser |
| `#pull-requests` | PR host, title format, CI watch, review-bot loop | releaser |
| `#pr-template` | the PR body the team uses | releaser, commenter |
| `#deploy` | the environments, what triggers each, how a deploy is dispatched and watched | releaser |
| `#release` | version scheme, release branches and tags, the procedure, which steps are the human's | releaser |
| `#demo` | the demo label, integration branch, and environment — or that there is no demo cadence | releaser |
| `#announcements` | where releases, deploys, and incidents are announced, and who may post | releaser, commenter |
| `#observability` | the platform, how to query it, credentials, per-platform traps | architect, backend-dev |
| `#gotchas` | destructive commands, production-access rules, traps specific to this workspace | everyone |

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
<remote name + default branch = the base ref (e.g. origin/main); naming, worktree dependency wiring, push quirks>

<a id="dependency-order"></a>
## Dependency order
<providers before consumers; how a shared library is versioned and released>

<a id="commands"></a>
## Commands
<per-area table: narrowed tests (tester's) | the dev role's verification commands, named exactly; plus full suite, formatter traps>
<a command not in that table is not a verification gate; say so, or a role will count one>
<migrations: where they live, the generator command, and whether an applied revision may be
 hand-edited or renumbered — reviewer check 7 has nothing to cite if this is unstated>
<a id="parallel-tests"></a>
<one lane per area; the parallel flag each runner takes; suites that must stay sequential>

<a id="style"></a>
## Style
<per language; import rules>
<a id="layering"></a>
<layering gate, if any>

<a id="tests"></a>
## Tests
<framework, naming, location, coverage gate, mocking policy>
<who runs them and when — dev roles write, tester runs at step 5, CI runs the full suite>

<a id="stack"></a>
## Local stack
<how to run everything, how to point it at a worktree, ports, health check, teardown>
<a id="stack-limits"></a>
### Stack limits
<what a green run does not prove>

<a id="tracker"></a>
## Tracker
<URL, project key, CLI or API, auth verification, allowed writes and workflow transitions — or "no transitions; state is the humans'" and what replaces them — attachments>

<a id="pull-requests"></a>
## Pull requests
<host, title format, CI watch command, review-bot loop>
<a id="pr-template"></a>
### PR body
<the template>

<a id="deploy"></a>
## Deploy
<environments, what triggers each, the dispatch and watch commands, what a failed run leaves behind>

<a id="release"></a>
## Release
<version scheme, release branch and tag naming, the ordered procedure, which steps only the human does>

<a id="demo"></a>
## Demo prep
<demo label, integration branch, environment — or one line saying there is no demo cadence here>

<a id="announcements"></a>
## Announcements
<each channel, what posts automatically, what a role may post and what needs the human's go-ahead>

<a id="observability"></a>
## Observability
<platform, where it is wired in, how to query it, whether credentials exist locally at all>

<a id="voice"></a>
## Voice
<who the text sounds like, with do/don't examples>

<a id="gotchas"></a>
## Gotchas
<destructive commands, masked failures, environment traps, production-access rules>
```

## Rules for writing it

- **One home per fact.** If it is here, no role file repeats it — roles link.
- **Say no explicitly.** "No transitions", "no review bot", "no build step", "one repo, one PR" are answers; `llm/` branches on them. Silence reads as the generic default and produces a role doing something this workspace forbids.
- Commands are copy-pasteable, with the environment variables they need.
- Name what a green result does *not* prove; that is the section roles get wrong most.
- If the organisation has no equivalent of a section (no layering, no local stack), keep the anchor and say so in one line. A missing anchor breaks links; an honest "not applicable" does not.

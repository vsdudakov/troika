# PROFILE.template.md

The project profile every workspace must provide. `/tr:setup` writes it for you: it reads your repos, drafts every section it can prove, asks about the rest, and saves the result as `<workspace>/.troika/PROFILE.md`. Filling it in by hand is the same job — copy this skeleton there, and delete the guidance in angle brackets.

Troika ships as a plugin, so its roles and skills live in the host's plugin cache, not in your workspace — `${CLAUDE_PLUGIN_ROOT}` is where a running command finds them. Nothing in them names your organisation: they cite **this** file **by anchor**, as `` `#tracker` ``. Keep the anchor ids below exactly as written — the headings above them are yours to reword. An anchor with no content is a role reading a dead reference.

Write no path to the plugin's own tree here. A role reads its procedure from `${CLAUDE_PLUGIN_ROOT}`, and everything it *writes* from the resolver's `$TROIKA_*` variables ([`#workspace-paths`](#workspace-paths)); a literal `troika/...` in this file is a path that is right in one install and wrong in every other.

| Anchor | Must answer | Read by |
| --- | --- | --- |
| `#rules` | the rules that bind every session, with or without a role | everyone |
| `#comments` | when a comment is allowed in code | dev roles, reviewer |
| `#no-ai-attribution` | what may never appear in commits, PRs, tracker text | everyone |
| `#voice` | how outward-facing text sounds | commenter |
| `#repo-map` | which repos exist, what each is, what is out of scope | everyone |
| `#ownership` | which role owns which repo or app | everyone |
| `#autonomy` | **who the reporter is and how `--ask` reaches them**, how long a run waits, and the decisions that may never be automatic on an unattended run | orchestrator, architect, reviewer, releaser |
| `#loops` | **the loop cap: how many fix → re-review cycles any loop runs before it stops and reports** — default 3 | everyone |
| `#models` | **the model and effort each role runs on, per host** — the values the orchestrator passes at spawn | orchestrator, everyone |
| `#review-runner` | **which tool runs an independent review pass, and the exact command** — or an explicit "there is none" | reviewer |
| `#workspace-paths` | the workspace root, the resolver, and the absolute-path rule | everyone |
| `#code-search` | the code search tool and how to refresh its index | architect, dev roles, reviewer, tester |
| `#branches` | **remote name and default branch (the base ref every diff and worktree uses)**, branch naming, worktree dependency setup, push quirks | dev roles, reviewer, tester, releaser |
| `#dependency-order` | provider → consumer order across repos, and how shared libraries are released | architect, releaser |
| `#commands` | per repo or area: narrowed tests, **the exact verification commands a dev role must run as its gate** (lint, and a type check or build only if that is how this workspace runs it), full suite, per-runner parallel flags; and for migrations, **the generator command plus what may be done to a revision that has already been applied** | dev roles, reviewer, tester |
| `#parallel-tests` | one lane per area, the parallel flag each runner takes, suites that must stay sequential | tester |
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
# PROFILE.md — <Org>

The project profile for Troika. Roles reference these sections by anchor; Troika itself is installed as a plugin and is not part of this workspace.

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

<a id="autonomy"></a>
## Autonomy
<a run is unattended unless it is started with `--ask`, which stops after the plan is approved (or the bug is reproduced) and waits for the reporter. Say here whether this team expects `--ask` on every ticket, on some kinds of ticket, or never — it is a norm the humans hold each other to, not a switch.>
<who the reporter is: the ticket's reporter field, the requester, a named role — and where they are asked (a tracker comment, a chat channel, the terminal the run started in)>
<how long an `--ask` run waits for them, and what happens when the wait runs out — proceed and say so, or stop. Silence is not a decision; say which one it is here.>
<the decisions that may never be automatic — this list is what keeps an unattended run honest, so fill it even if every run here uses `--ask`. Suggested floor, edit it:>
<- a change to what the ticket asked for — scope, or user-visible behaviour nobody signed off>
<- a destructive or irreversible migration, and any data backfill that cannot be replayed>
<- a change to a public API contract other teams consume>
<- a production deploy, and anything that touches production data>
<running unattended never silences a stop condition: a cap that is hit, an unowned repo or an unreproducible bug still stops the run.>

<a id="loops"></a>
## Loop cap
<how many cycles any fix → re-review loop runs before it stops and reports: the plan-review rewrite loop, the internal-review fix loop, the unit-test fix loop, the QA fix loop, the PR review loop, the review-bot waves. One number for all of them; default 3 when this section names none. A hit cap is a stop condition, never silently exceeded.>

<a id="models"></a>
## Models and effort
<one row per role, one column per host you actually use. These are the values the orchestrator passes at spawn; nothing reads them from a role file.>
<the defaults below are Troika's shipped starting point — replace the ids with what your accounts can run, and verify each id exists before pinning it>

| Role | Claude model (fallback) | Claude effort | Codex model | Codex effort |
| --- | --- | --- | --- | --- |
| architect | `claude-fable-5` → `claude-opus-5` | high | `gpt-5.6-sol` | high |
| backend-dev | `claude-fable-5` → `claude-opus-5` | high | `gpt-5.6-sol` | high |
| frontend-dev | `claude-sonnet-5` | medium | `gpt-5.6-sol` | medium |
| reviewer | `claude-fable-5` → `claude-opus-5` | high | `gpt-5.6-sol` | high |
| tester | `claude-sonnet-5` | medium | `gpt-5.6-sol` | medium |
| qa | `claude-sonnet-5` | medium | `gpt-5.6-sol` | medium |
| releaser | `claude-sonnet-5` | low | `gpt-5.6-sol` | medium |
| commenter | `claude-fable-5` → `claude-opus-5` | low | `gpt-5.6-sol` | low |

<`→` means fallback: the second id is used where the first is unavailable>
<each role file states what its row *needs* — judgment tier or execution tier, and why — and when to raise either dial; the ids and efforts themselves live here and only here>
<a host with no effort control: say so, and say which model tier stands in for a `high`+ role>
<an effort above is the *first* pass's. A pass re-entering a gate after a fix runs one tier down, because it reads only what the fix changed; a widened cycle and the last cycle the loop cap allows keep the row's effort. Say here if this workspace wants that flat instead, and why.>

<a id="review-runner"></a>
### Review runner
<the tool that runs the plan and internal review passes independently, and the exact command, so the reviewer is not the family that wrote the work>
<e.g. `codex exec -m gpt-5.6-sol -c model_reasoning_effort="high" -` for the plan pass and `codex exec review --uncommitted -` for the diff pass>
<if this workspace has only one model family available, say "no separate runner" and name what replaces it — a fresh session on the reviewer row, with no memory of writing the work>

<a id="workspace-paths"></a>
## Workspace paths
<the workspace root, and the rule that every path below it is used absolute>
<the five variables the plugin's resolver exports, and what each holds here:>
<`$TROIKA_WORKSPACE` · `$TROIKA_PROFILE` · `$TROIKA_WORKTREES` · `$TROIKA_SCRATCHPAD` · `$TROIKA_MEMORY`>
<resolve them once per session: eval "$(python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --ensure)">
<the `/tr:*` commands already run that as their first step; spell it out here for a role or script started outside one>
<their values come from `<workspace>/.troika/settings.json`, written by /tr:setup — the one place a path is declared>
<and: a non-zero exit from the resolver means stop, not guess>

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
<migrations: where they live, the generator command, and whether an already-applied revision may be hand-edited or renumbered — the reviewer's migrations check has nothing to cite if this is unstated>
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

- **One home per fact.** If it is here, no role file repeats it — roles link. The reverse also holds: nothing about Troika's own layout belongs here, because the plugin carries it.
- **Say no explicitly.** "No transitions", "no review bot", "no build step", "one repo, one PR" are answers; the procedures branch on them. Silence reads as the generic default and produces a role doing something this workspace forbids.
- Commands are copy-pasteable, with the environment variables they need.
- Name what a green result does *not* prove; that is the section roles get wrong most.
- If the organisation has no equivalent of a section (no layering, no local stack), keep the anchor and say so in one line. A missing anchor breaks links; an honest "not applicable" does not.

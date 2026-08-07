# Toy workspace profile

A filled [project profile](../../PROFILE.template.md) for the fault-injection fixtures. Small on purpose,
but it carries **every anchor** the `agents/` and `skills/` trees link to — a role reading a dead
link here would fail the test for the wrong reason. `tests/run.py --check` verifies that.

<a id="repo-map"></a>
## Repo map

One repo, `toyapp`, at `<workspace>/toyapp`. Python. No client app, no extension, no compiled service.

<a id="ownership"></a>
## Ownership

| Path | Owner |
| --- | --- |
| `app/api/**` · `app/service/**` · `app/repository/**` · `app/models.py` | backend-dev |
| `migrations/**` · `tools/**` | backend-dev |
| `tests/**` | backend-dev |

No frontend role applies here. Nothing is out of scope.

<a id="dependency-order"></a>
## Dependency order

One repo, so the order is trivial: `toyapp`.

<a id="branches"></a>
## Branches

- Remote `origin`, default branch `main`. `<BASE>` is `origin/main`.
- Branch names: `<TICKET>-<short-description>`, ticket key uppercase.
- No dependency symlinks — the toy repo has no third-party dependencies and no `.env`.
- Nothing is pushed to `main` directly.

<a id="rules"></a>
## Rules

- Imports at the top of the file. An import inside a function or method is a defect, not a style choice.
- No secrets, no `.env`, no debug prints, no commented-out code.

<a id="comments"></a>
## Comments

Comments explain a non-obvious **why**. A comment restating the code is a nit, every time. Docstrings are not comments and stay.

<a id="style"></a>
## Style

PEP 8, 100-column lines, type hints on every public function. `snake_case` for functions, `PascalCase` for classes.

<a id="layering"></a>
## Layering

`api → service → repository → models`. Each layer calls only the one directly below it.

**An `api` module importing `repository` or `models` directly is a layering violation** — it skips `service`. Wrong even when it works.

<a id="tests"></a>
## Tests

- Framework: `pytest`.
- **Mirror path**: `app/<path>/<name>.py` is tested by `tests/<path>/test_<name>.py`. Every changed or created source file has one.
- Tests assert real behaviour, not that a mock was called. Only external services may be mocked; the toy repo has none, so **nothing may be mocked**.
- GIVEN / WHEN / THEN comments in each test body.

<a id="commands"></a>
## Commands

One area, `toyapp`, run from the repo root:

| Purpose | Command |
| --- | --- |
| Lint (verification gate) | `python3 -m compileall -q app tests` |
| Test collection (no execution) | `python3 -m pytest --collect-only -q` |
| Unit tests | `python3 -m pytest -q` |
| Migrations | `python3 tools/make_migration.py <name>` |

No separate type check and no build step. Run the lint command and nothing else as the dev gate.
Run the commands in this table as written; a command that is not in it is not a verification gate,
and the log of one does not stand in for the lint command's.

**Migrations** live in `migrations/`, one numbered revision per file, and are produced only by
`python3 tools/make_migration.py <name>`. `migrations/0001_initial.py` is applied in every
environment. **An applied revision is history: it is never hand-edited and never renumbered.**
A schema change is a new revision from the generator.

<a id="parallel-tests"></a>
## Parallel tests

No parallel flag. The suite is sequential.

<a id="code-search"></a>
## Code search

`grep -rn` from the repo root. No index to refresh.

<a id="gotchas"></a>
## Gotchas

- The toy repo has no installed dependencies, so no worktree symlink step applies.
- `python3 -m compileall` returns 0 on an empty file list — check that it named the files you changed.

<a id="stack"></a>
## Local stack

`python3 -m app.api.routes` from the repo root, serving on `127.0.0.1:8099`. Health check: `GET /healthz` returns `200 {"ok": true}`. Reset: stop the process; there is no datastore to clear.

<a id="stack-limits"></a>
## Stack limits

The toy stack has an in-memory store, so it proves nothing about migrations or about concurrent writes. Both ship on unit tests alone.

<a id="tracker"></a>
## Tracker

**No tracker.** There is no CLI, no API, no auth check, and **no transitions** — the board's state does not exist. Every "transition the ticket" instruction in a procedure means: do nothing. The ticket is the plan file at `$TROIKA_SCRATCHPAD/plans/<TICKET>.md`.

<a id="pull-requests"></a>
## Pull requests

**No PR host.** Nothing is pushed and no PR is opened in these fixtures; the flow stops at the internal review. There is **no review bot**, so no automated-review gate applies. CI watch command: none.

<a id="pr-template"></a>
## PR body

Not used — see Pull requests.

<a id="release"></a>
## Release

No release cadence. [release-cut](../../skills/release-cut/SKILL.md) does not apply here.

<a id="deploy"></a>
## Deploy

No deploy. [demo-prep](../../skills/demo-prep/SKILL.md) does not apply here.

<a id="demo"></a>
## Demo prep

No demo label, no integration branch. Does not apply.

<a id="announcements"></a>
## Announcements

None.

<a id="observability"></a>
## Observability

No platform. [incident-triage](../../skills/incident-triage/SKILL.md) does not apply here.

<a id="voice"></a>
## Voice

Plain, factual, no exclamation marks, no emoji. Nothing leaves the workspace in these fixtures anyway.

<a id="no-ai-attribution"></a>
## No AI attribution

No AI product is ever named or hinted at — not in code, comments, commit messages, trailers, or any generated text. Strip anything the tooling appends.

<a id="workspace-paths"></a>
## Workspace paths

`TROIKA_WORKSPACE` is the workspace root — the directory holding `.troika/` and `toyapp/`. Every scratchpad path is absolute.

<a id="models"></a>
## Models and effort

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

`→` means fallback. The fixtures run whatever `TROIKA_CMD` names, so these rows are what a real workspace would declare, not what the harness spawns.

<a id="review-runner"></a>
### Review runner

Plan pass: `codex exec -m gpt-5.6-sol -c model_reasoning_effort="high" -`. Diff pass: `codex exec review --uncommitted -`, and `--base <BASE>` for work already committed. The fault-injection cases feed the prompt on stdin themselves, so a case never shells out to it.

<a id="autonomy"></a>
## Autonomy

No reporter and no channel exist for a toy workspace, so `--ask` is never used here and every fixture case runs unattended: the reporter review at 2r never runs.

Never automatic: a change to what the case asks for, a destructive migration, or anything outside `toyapp`. Those stop the run, `--ask` or not.

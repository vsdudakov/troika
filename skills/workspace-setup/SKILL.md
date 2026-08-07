---
name: workspace-setup
description: Creates a workspace — the .troika directory, its settings, and the profile every other procedure reads — by investigating the repos first and asking only what they cannot answer.
---

# Workspace setup (create `.troika/`, write the profile)

A folder of repos in, a working workspace out: `.troika/settings.json`, the state directories, and a filled-in `.troika/PROFILE.md`. Every other Troika procedure stops immediately without this, so it is the first thing run in a new workspace and the only procedure that may run outside one.

**Kind** procedure · **Used by** [architect](../../agents/architect.md) · **When** Troika has just been installed, a new folder of repos is being adopted, or the profile has drifted from how the repos actually work · **Ends with** `.troika/settings.json`, the three state directories, and `$TROIKA_PROFILE` written with every anchor answered

The rule that shapes it: **read before you ask.** Style, tests, commands, branches and the local stack are already written down in the repos — derive them from the code and show the draft. Ask only what no file records: which repos are in scope, who reviews, which tracker, which tools, and how the team sounds.

| Step | What it does | Advance only when |
| --- | --- | --- |
| [1](#root) | fix the workspace root | the root holds the repos and is not itself a repo |
| [2](#scope) | list every repo, **ask which ones Troika covers** | the caller has ticked the list |
| [3](#scaffold) | `resolve.py --init` — settings, state dirs, `.gitignore` | the three directories exist |
| [4](#derive) | derive style, tests, commands, stack, branches, layering from the code | every in-scope repo has been probed, and gaps are named |
| [5](#credentials) | find the tracker, GitHub and tool credentials already on this machine | each one is found, or its question is queued for step 6 |
| [6](#ask) | one batched interview for what no file records | every question has an answer or an explicit "not applicable" |
| [7](#write) | draft, confirm once, write, verify the anchors | every template anchor exists in the written profile |

Never print a secret's **value**. The profile records the variable name and where it lives — `$JIRA_API_TOKEN`, exported from `~/.zshrc` — never the token itself.

<a id="root"></a>
## 1. Fix the workspace root

The workspace is the folder that **holds** the repos, never a repo itself. Its state directories sit beside them, and its profile describes all of them at once.

1. The argument is that folder; with none, use the current directory.
2. If the chosen directory is itself a git repository (`git rev-parse --show-toplevel` returns it), say so and propose its parent. **Ask before using either** — a workspace created one level too deep puts worktrees inside the repo they check out.
3. If `.troika/settings.json` or the profile already exists, go to [re-runs](#rerun) and ask before writing anything.

<a id="scope"></a>
## 2. Scope — which repos Troika covers

List every immediate subdirectory that is a git repository, with one line of evidence each: its stack from the manifest, its remote, its default branch. **No repos is a stop** — there is nothing to write a profile about.

Then ask, as a ticked list the caller edits rather than an open question:

> Troika will cover these repositories. Untick anything it should never touch.
>
> - [x] `backend` — Python 3.13 · Django · `origin/main`
> - [x] `frontend` — TypeScript · React + Vite · `origin/main`
> - [ ] `infra` — Terraform · <untick if roles must never open it>

An unticked repo is not forgotten: it goes into `#repo-map` **by name**, marked out of scope, so a role that stumbles on it knows it was a decision. Only ticked repos are probed in step 4.

<a id="scaffold"></a>
## 3. Scaffold — settings, state directories, .gitignore

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --init <root>
eval "$(python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --ensure --from <root>)"
```

`--init` writes `settings.json` with every path spelled out, a `.gitignore` covering the three state directories, and creates them. It changes nothing that already exists.

Then raise the one thing the defaults cannot know: **state outside the workspace.** A slow disk, or a workspace on a network mount — `scratchpad`, `worktrees` and `memory` each take an absolute path in `settings.json`. Moving them later is one edit; moving them after a flow has written to them strands its files.

<a id="derive"></a>
## 4. Derive from the code — one probe per repo, all at once, read-only

Fan out: one probe per in-scope repo. A probe reads and reports with `file:line`; it decides nothing and writes nothing. **Read the code itself, not only the config** — a linter config says what is enforced, the code says what the team actually does.

<a id="derive-style"></a>
### Style — `#style`, `#layering`

Read the linter and formatter config **and** three or four real source files per language, backend and frontend separately. Write down what a reviewer could cite:

| Read | Produces |
| --- | --- |
| `ruff.toml`, `.eslintrc*`, `biome.json`, `.golangci.yml`, `.editorconfig`, `pyproject.toml` | the rules already enforced, and the line length |
| the largest service or component file in each language | typing and docstring habits, naming, logging shape, import discipline |
| the directory tree under the source root | where a component, hook, type, migration or command is expected to live |
| the deepest call chain you can follow — handler to storage | the layers, and whether a handler is allowed to touch storage directly |

State each rule as something a review can fail on: *"every function is typed; `X | None`, never `Optional`"*, not *"the code is typed"*. Where the code disagrees with the linter, record the code and say the linter disagrees.

<a id="derive-tests"></a>
### Tests — `#tests`, `#parallel-tests`

Read the test tree and **open two or three real tests**, not just the config:

- the framework and runner, from the manifest and CI;
- where a source file's test lives — the mirror rule, spelled out as a path pattern;
- naming, and the body convention (GIVEN/WHEN/THEN, docstring, comment, or none);
- what the existing tests mock and what they do not — the mocking policy, in one sentence;
- the coverage gate, or that there is none, and which command is the real gate;
- which suites can run in parallel and which must not.

<a id="derive-stack"></a>
### Local stack — `#stack`, `#stack-limits`

Derive a **runnable** sequence for the ticked repos together, not a description of one:

| Read | Produces |
| --- | --- |
| `docker-compose*.yml`, `Procfile`, `Tiltfile`, dev `Makefile` targets | the exact commands, in order, and what each one starts |
| `.env.example`, `settings/*.py`, `vite.config.*` | the variables the stack needs, and their dev defaults |
| the compose file's ports and healthchecks | how to know it is up, and on which URL |
| seed or fixture commands | how to get data a QA run can act on |

Write it as: bring up, point at a worktree, health check, seed, tear down. Then name what a green local run **cannot** prove — anything the compose file stubs, anything only staging has. Where the stack cannot be derived, say so in one line rather than inventing it; QA reads that line and plans around it.

<a id="derive-rest"></a>
### The rest

| Read | Answers |
| --- | --- |
| `README`, top-level directories | `#repo-map` |
| `Makefile`, `Taskfile`, `justfile`, `package.json` scripts, CI workflows | `#commands` — the exact lint, type-check, build, test invocations, and which the team treats as a gate |
| `git remote -v`, `git symbolic-ref refs/remotes/<remote>/HEAD`, recent branches, existing long-lived branches | `#branches` — remote, default branch, naming, and any `staging`-like branch |
| CI workflows and deploy config | `#deploy`, `#release` |
| `.github/PULL_REQUEST_TEMPLATE.md`, `CONTRIBUTING.md` | `#pr-template`, `#pull-requests` |
| cross-repo dependency pins | `#dependency-order` |
| migration directory and its helpers | `#commands` — the generator, and what may be done to an applied revision |
| observability and error-reporting dependencies | the candidate list step 6 offers |
| an existing `AGENTS.md`, `CLAUDE.md`, `.cursorrules` | any anchor — reuse verbatim rather than restating |

**A probe that finds nothing says so.** "No CI in this repo" is an answer the profile needs; a silently skipped anchor is one a role later reads as a dead reference.

<a id="credentials"></a>
## 5. Credentials — find what is already here before asking for it

Read-only, and **never print a value**. Record the variable name and its source file.

```bash
gh auth status                                    # GitHub: already authenticated?
gh auth token >/dev/null 2>&1 && echo "gh token present"
env | cut -d= -f1 | grep -iE 'token|api_key|dsn|jira|trello|linear|sentry|datadog|dd_|aws_'
grep -lE 'export [A-Z_]*(TOKEN|API_KEY|DSN)' ~/.zshrc ~/.bashrc ~/.profile ~/.zprofile 2>/dev/null
```

| Found | Then |
| --- | --- |
| `gh` is authenticated | record it; no question |
| a tracker token in the environment or a shell file | show **the variable name and the file**, and ask "use this one?" |
| an observability key for a tool the manifests mention | same — name and file, confirm |
| nothing | queue the question for step 6: *how does this machine get a token for X?* |

A found credential is never copied into the profile. The profile says: *"`$JIRA_API_TOKEN`, exported from `~/.zshrc`; `curl -u $JIRA_EMAIL:$JIRA_API_TOKEN` to verify"*.

<a id="ask"></a>
## 6. Ask — one batch, defaults pre-filled

Ask everything at once, with what step 4 and 5 drafted already filled in, so most answers are a confirmation. Ask in the caller's own language.

**1. Who reviews — `#review-runner`**

> The plan and the diff are reviewed by a **different model family** from the one that wrote them. Which tool should run that pass?
>
> - [ ] Codex CLI — `codex exec -m <model> -c model_reasoning_effort="high" -`, and `codex exec review --uncommitted -` for a diff
> - [ ] Gemini CLI · Cursor · another agent that reads a prompt on stdin — give the command
> - [ ] None available — the pass runs in a fresh session on the reviewer's own row

**2. Branches — `#branches`, `#demo`** (explain both; they are not obvious)

> - **Base branch** — the branch every feature branches from and every PR targets, and the ref every diff, worktree and review is measured against. Detected: `origin/main`.
> - **Demo branch** — a throwaway integration branch some teams reset before a demo and merge selected PRs onto, never merged back. Detected: `staging`. If there is no demo cadence here, say so and `#demo` records that.

**3. Tracker — `#tracker`**

> Which tracker? (Jira · Linear · Trello · GitHub Issues · none.) Its URL and project key. Found `$JIRA_API_TOKEN` in `~/.zshrc` — use it? If not, how does this machine get one?
>
> And the answer that matters most: **which writes may a role make?** The transition names, or an explicit "there are none" and what replaces them. Silence here reads as "the usual transitions" and a role moves somebody else's ticket.

**4. Investigation tools — `#observability`**

> Which of these can we use when investigating production? Tick all that apply.
>
> - [ ] Sentry · [ ] Datadog · [ ] Grafana / Loki · [ ] Kibana / OpenSearch
> - [ ] AWS CloudWatch · [ ] GCP Cloud Logging · [ ] Azure Monitor
> - [ ] New Relic · [ ] Honeycomb · [ ] Rollbar · [ ] Bugsnag · [ ] Better Stack
> - [ ] None — production is not readable from here

For each ticked tool: the query command or URL, and the credential — the one step 5 found, or how to get it. A ticked tool with no credential is written down as *"selected, not usable yet"*, because that is what a role hitting it will find.

**5. Voice — `#voice`**

> Paste two or three sentences you have actually written to your team — a PR description, a ticket comment, a Slack message. Not an example of how you would like to sound; a real one.

Derive from them: sentence length, formality, whether emoji appear, whether the team writes British or American English, how a change is announced. Write one *do* and one *don't* with a rewritten example, and confirm.

**6. The rest, in the same batch**

- **`#ownership`** — which role owns which repo or app. Drafted from the stacks found; a repo nobody owns is a legitimate answer and must be named.
- **`#gotchas`** — destructive commands, production-access rules, the traps a newcomer hits. People list these readily and no file records them.
- **`#stack-limits`** — what QA has to check by hand today because the local stack cannot prove it.
- **`#rules`** — anything binding beyond Troika's own defaults: signing, ask-before-committing, branch policy.
- **`#autonomy`** — who the reporter is and how `--ask` reaches them, how long a run waits, and what may **never** be automatic on an unattended run. Offer the template's floor and let them add to it.
- **`#models`** — show the template's default table and ask only for corrections: an id an account cannot run fails at spawn, and every role is spawned from that table.

Ask only when the evidence was silent or ambiguous: `#release` (the steps only a human does), `#deploy` (who may dispatch one), `#announcements`, `#code-search`.

Never ask for `#workspace-paths` or `#no-ai-attribution`: the first is the resolver's own contract and is written mechanically, the second is Troika's rule and is stated, not negotiated.

Where an answer does not come, write the anchor with an honest one-line "not applicable here" or "unknown — ask before relying on this". **Never leave an anchor empty and never delete one**: every role reads the profile by anchor, and a missing one is a dead reference in the middle of a flow.

<a id="write"></a>
## 7. Draft, confirm, write

1. Read the template — `${CLAUDE_PLUGIN_ROOT}/PROFILE.template.md`. It carries both the anchor contract and the skeleton.
2. Fill every anchor from steps 4, 5 and 6. Commands are copy-pasteable with the variables they need. Keep the anchor ids exactly as the template spells them; the headings above them may be reworded.
3. **Show the caller the draft before writing it** — one gate, whole file. Not anchor by anchor: the point of reading first was to spend one confirmation, not twenty-nine.
4. Write it to `$TROIKA_PROFILE`.

Then verify, and report the result:

```bash
grep -o 'id="[a-z-]*"' "$TROIKA_PROFILE" | sort -u     # every anchor the roles cite must appear
eval "$(python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --ensure)"
```

An anchor in the template with no counterpart in the written profile is a failure of this step, not a nit.

<a id="rerun"></a>
## Re-runs — ask first, never assume

A second run is far more likely to be a mistake — the wrong directory, or a caller who did not
know setup had already been done here — than a deliberate rewrite. So say what is already
there and stop for an answer:

> This workspace is already set up: `.troika/settings.json` and `.troika/PROFILE.md`, last
> changed <date>. What would you like to do?
>
> 1. **Nothing** — leave it as it is.
> 2. **Update it** — re-read the repos and propose a diff against what the profile says now.
> 3. **Rewrite the profile** — start from the template and go through setup again. Everything
>    written by hand is lost.

Default to 1. Never take 3 without the caller choosing it in words, and say plainly what it
discards before doing it.

On **update**, run step 4 again and propose a diff: anchors whose evidence has changed, and
anchors that are missing entirely — a profile written before an anchor existed is the common
case, and it reads as a dead reference to every role that cites it. Confirm the diff, then
apply it. Everything a human wrote — voice, gotchas, tracker rules — survives untouched unless
they say otherwise.

Report the existing files even when the answer is 1. A run that changes nothing and says
nothing is indistinguishable from a fresh install that worked.

## Output

```markdown
### Workspace setup: <root>
- Repos covered: <repo — stack · …> — out of scope: <repo — why, or none>
- Written: `.troika/settings.json` · state directories · `<profile path>` — <or "already present, unchanged">
- State outside the workspace: <which paths, or none>
- Derived from the code: <anchor · … — count>
- Credentials found: <name and source, per tool> — <and which are still missing>
- Answered by you: <anchor · … — count>
- Unresolved: <anchor — why, and what to do about it — or none>
- Next: `/tr:dev <TICKET>` for a full pipeline, or `/tr:spike <TICKET>` to plan one first
```

## Stop conditions

Stop and report when: the chosen root holds no git repository; the root is a repo and the caller has not said whether to use it or its parent; every repo was unticked at step 2; `--init` cannot write (permissions, read-only mount); or the tracker's write rules cannot be established at all — a profile that guesses them is worse than one that says "unknown, ask first", so write the honest line and say plainly that it is unresolved.

Write no product code and touch no repo. This procedure creates one directory and one profile; a repo changed during setup is a change nobody reviewed.

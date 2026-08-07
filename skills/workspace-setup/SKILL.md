---
name: workspace-setup
description: Creates a workspace — the .troika directory, its settings, and the profile every other procedure reads — by investigating the repos first and asking only what they cannot answer.
---

# Workspace setup (create `.troika/`, write the profile)

A folder of repos in, a working workspace out: `.troika/settings.json`, the state directories, and a filled-in `.troika/PROFILE.md`. Every other Troika procedure stops immediately without this, so it is the first thing run in a new workspace and the only procedure that may run outside one.

**Kind** procedure · **Used by** [architect](../../agents/architect.md) · **When** Troika has just been installed, a new folder of repos is being adopted, or the profile has drifted from how the repos actually work · **Ends with** `.troika/settings.json`, the three state directories, and `$TROIKA_PROFILE` written with every anchor answered

The rule that shapes it: **read before you ask**. Most of the profile is already written down in the repos — manifests, CI workflows, linter configs, git remotes. Anything provable from a file is drafted from that file and shown for confirmation; the human is asked only about the things no repo records, such as which tracker writes a role may make and how the team's outward-facing text should sound.

<a id="root"></a>
## 1. Fix the workspace root

The workspace is the folder that **holds** the repos, never a repo itself. Its state directories sit beside them, and its profile describes all of them at once.

1. The argument is that folder; with none, use the current directory.
2. If the chosen directory is itself a git repository (`git rev-parse --show-toplevel` returns it), say so and propose its parent. **Ask before using either** — a workspace created one level too deep puts worktrees inside the repo they check out.
3. List its immediate subdirectories that are git repositories. **None is a stop**: there is nothing to write a profile about.
4. If `.troika/settings.json` or the profile already exists, this workspace is already set up — go to [re-runs](#rerun) and ask before writing anything.

Report the root and the repos found before doing anything that writes.

## 2. Scaffold — settings, state directories, .gitignore

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --init <root>
eval "$(python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --ensure --from <root>)"
```

`--init` writes `settings.json` with every path spelled out, a `.gitignore` covering the three state directories, and creates them. It changes nothing that already exists.

Then raise the one thing the defaults cannot know: **state outside the workspace.** A slow disk, or a workspace on a network mount — say that `scratchpad`, `worktrees` and `memory` each take an absolute path in `settings.json`, and set them now if the caller wants that. Moving them later is one edit; moving them after a flow has written to them strands its files.

Say what was written. If nothing was, say that too — a re-run that reports success while changing nothing reads as a fresh install.

<a id="investigate"></a>
## 3. Investigate — one read-only probe per repo

Fan out: one probe per repo, all at once, each reading only. A probe reports evidence with `file:line`; none of them decides anything, and none writes.

Each probe reads what its repo actually has and returns what it proves:

| Read | Answers | Evidence looks like |
| --- | --- | --- |
| `README`, top-level directories | `#repo-map` | what the repo is, its stack, what it is not |
| manifests — `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Gemfile` | `#repo-map`, `#commands`, `#tests` | language, runner, script names |
| `Makefile`, `Taskfile`, `justfile`, `package.json` scripts | `#commands` | the exact lint, type-check, build and test invocations |
| CI — `.github/workflows/*`, `.gitlab-ci.yml`, `.circleci/` | `#commands`, `#tests`, `#deploy`, `#release` | what the team already treats as a gate, and what triggers each environment |
| linter and formatter config — `.eslintrc*`, `ruff.toml`, `.golangci.yml`, `.editorconfig` | `#style` | the rules already enforced, so the profile does not invent new ones |
| test tree and one representative test | `#tests` | framework, naming, where a source file's test lives, mocking habits |
| `git remote -v`, `git symbolic-ref refs/remotes/<remote>/HEAD`, recent branch names | `#branches`, `#pull-requests` | remote name, default branch, the naming pattern in use |
| `docker-compose*.yml`, `Procfile`, `.env.example`, dev make targets | `#stack` | how the product runs locally, its ports, its dependencies |
| `.github/PULL_REQUEST_TEMPLATE.md`, `CONTRIBUTING.md` | `#pr-template`, `#pull-requests` | the body the team already uses, and its review rules |
| cross-repo dependency pins — one repo's manifest naming another | `#dependency-order` | which repo is the provider and which the consumer |
| observability and error-reporting dependencies in the manifests | `#observability` | the platform, if there is one |
| an existing `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, or agent doc | any anchor | rules the team already wrote for agents — reuse them verbatim rather than restating them |

**A probe that finds nothing says so.** "No CI in this repo" is an answer the profile needs; a silently skipped anchor is one a role later reads as a dead reference.

Also record what the evidence *cannot* settle, per anchor, because that list is exactly step 4's questions.

<a id="ask"></a>
## 4. Ask — only what the repos do not record

Batch the questions; do not interview anchor by anchor. For each, offer the drafted default so the answer can be a confirmation.

Always ask, because no repo records them:

- **`#tracker`** — URL, project key, the CLI or API, how to verify auth, and **which writes a role may make**: the transition names, or an explicit "there are none" plus what replaces them. This is the one whose silence causes the most damage, because a role reads silence as "the usual transitions" and moves someone else's ticket.
- **`#ownership`** — which role owns which repo or app. Draft it from the stacks found and confirm; a repo nobody owns is legitimate, and must be named as such.
- **`#voice`** — how outward-facing text should sound, with one do and one don't.
- **`#gotchas`** — destructive commands, production-access rules, the traps a newcomer hits. Ask for them by that name; people list them readily and no file contains them.
- **`#stack-limits`** — what a green local run does not prove. Ask what QA has to check by hand today.
- **`#rules`** — anything binding beyond Troika's own defaults: signing, ask-before-committing, branch policy.
- **`#autonomy`** — a run is unattended unless it is started with `--ask`, so ask who the reporter is, where `--ask` reaches them, how long it waits, and what happens when the wait runs out. Ask separately for what may **never** be automatic — offer the template's floor and let them add to it; silence there is what turns an unattended run into an unreviewed one.
- **`#models`** — which hosts this workspace actually runs roles on, and whether the template's default model ids are available on those accounts. Show the default table and ask for corrections rather than for eight rows: an id that does not exist fails at spawn, and every role reads its model from here.
- **`#review-runner`** — which second tool runs the reviewer's plan and diff passes, so the reviewer is not the family that wrote the work, with the exact command. "We only have one family" is a valid answer; write it as such, with the fresh-session fallback named.

Ask only when the evidence was silent or ambiguous: `#demo`, `#announcements`, `#release` (the steps only a human does), `#deploy` (who may dispatch one), `#layering`, `#code-search`.

Never ask for `#workspace-paths` or `#no-ai-attribution`: the first is the resolver's own contract and is written mechanically, the second is Troika's rule and is stated, not negotiated.

Where an answer does not come, write the anchor with an honest one-line "not applicable here" or "unknown — ask before relying on this". **Never leave an anchor empty and never delete one**: every role reads the profile by anchor, and a missing one is a dead reference in the middle of a flow.

## 5. Draft, confirm, write

1. Read the template — `${CLAUDE_PLUGIN_ROOT}/PROFILE.template.md`. It carries both the anchor contract and the skeleton.
2. Fill every anchor from steps 3 and 4. Commands are copy-pasteable with the environment variables they need. Keep the anchor ids exactly as the template spells them; the headings above them may be reworded.
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

On **update**, run step 3 again and propose a diff: anchors whose evidence has changed, and
anchors that are missing entirely. Confirm the diff, then apply it. Everything a human wrote —
voice, gotchas, tracker rules — survives untouched unless they say otherwise.

Report the existing files even when the answer is 1. A run that changes nothing and says
nothing is indistinguishable from a fresh install that worked.

## Output

```markdown
### Workspace setup: <root>
- Repos: <repo — stack · …>
- Written: `.troika/settings.json` · state directories · `<profile path>` — <or "already present, unchanged">
- State outside the workspace: <which paths, or none>
- Drafted from evidence: <anchor · … — count>
- Answered by you: <anchor · … — count>
- Unresolved: <anchor — why, and what to do about it — or none>
- Next: `/tr:dev <TICKET>` for a full pipeline, or `/tr:spike <TICKET>` to plan one first
```

## Stop conditions

Stop and report when: the chosen root holds no git repository; the root is a repo and the caller has not said whether to use it or its parent; `--init` cannot write (permissions, read-only mount); or the tracker's write rules cannot be established at all — a profile that guesses them is worse than one that says "unknown, ask first", so write the honest line and say plainly that it is unresolved.

Write no product code and touch no repo. This procedure creates one directory and one profile; a repo changed during setup is a change nobody reviewed.

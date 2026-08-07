#!/usr/bin/env python3
"""Generates the slash commands from skills/.

`skills/<name>/SKILL.md` is the procedure itself, in the shape all three hosts discover a
skill in — no wrapper, no second copy. What that shape cannot express is a *command*: an
entry in the `/` menu, with an argument hint, that resolves the workspace before it starts.
So the procedures a caller *starts* a session with get `plugin/commands/<alias>.md`, and
that file is the only generated one.

Not every procedure earns a command. The steps `develop-flow` runs for you — plan-review,
implement-change, internal-review, run-unit-tests, qa-verify, release-pr — are read as
`SKILL.md` by the role running them, so a `/` entry for each only crowds the menu with
entry points that are wrong to start on their own. They stay skills: still discovered by
all three hosts, still invocable by name, just not in the `/` menu.

Commands are generated, never hand-edited: `tests/check.py` fails on any drift.

    python3 plugin/generate.py            # write the commands
    python3 plugin/generate.py --check    # exit non-zero if any is stale
"""

import glob
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# References and templates are read *by* a procedure, never run on their own, so only
# procedures become commands. A `/tr:pr-template` that fills nothing in would be a
# command that cannot be finished.
KIND = "procedure"


# skill directory -> (alias, argument hint). A procedure absent from this map gets no
# command; one present gets exactly one.
#
# The **alias** is what the caller types, so it is short and unambiguous across the whole
# map — `review` can only mean pr-review because internal-review and plan-review have no
# command at all.
#
# The **hint** is what the `/` menu shows next to it, and it is spelled out per command
# rather than defaulted: a hint inherited from a default is how `/tr:review` came to
# advertise `<TICKET>` for a procedure that reads a PR. One upper-case word, naming the
# thing the procedure's first step resolves — the accepted forms of that thing belong in
# the procedure, not in a menu line. `<>` is required, `[]` optional.
COMMANDS = {
    "workspace-setup": ("setup", "[PATH]"),
    "demo-prep": ("demo", "[LABEL]"),
    "develop-flow": ("dev", "<TICKET>"),
    "fix-pr": ("fix", "<PR>"),
    "incident-triage": ("triage", "<ISSUE>"),
    "pr-review": ("review", "<PR>"),
    "qa-verify": ("qa", "<PR>"),
    "release-cut": ("release", "<VERSION>"),
    "spike": ("spike", "<TICKET>"),
}


def skills():
    """(skill, alias, hint, description) per commanded procedure, in alias order."""
    out = []
    for path in sorted(glob.glob(str(ROOT / "skills" / "*" / "SKILL.md"))):
        name = os.path.basename(os.path.dirname(path))
        if name not in COMMANDS:
            continue
        text = Path(path).read_text(encoding="utf-8")
        kind = re.search(r"\*\*Kind\*\* (\w+)", text)
        if not kind or kind.group(1) != KIND:
            # A command whose target stopped being a procedure would read a file that no
            # longer describes a runnable one, so this is a failure, not a skip.
            raise SystemExit(f"{name} has a command but is not a {KIND}")
        desc = re.search(r"^description: (.+)$", text, re.M)
        if not desc:
            raise SystemExit(f"{name} has a command but no description")
        alias, hint = COMMANDS[name]
        out.append((name, alias, hint, desc.group(1).strip()))
    return sorted(out, key=lambda row: row[1])

# The body every command shares. Four numbered steps, in the order they must happen: the
# argument is stated first so a caller who typed nothing is stopped before the resolver
# runs, and the procedure is read before the profile so the profile is read for what the
# procedure actually asks of it.
BODY = """Run Troika's **{name}** procedure.

**Argument** — `{hint}`: $ARGUMENTS
{missing}

1. Resolve the workspace, before anything else:

   ```bash
   eval "$(python3 "${{CLAUDE_PLUGIN_ROOT}}/plugin/resolve.py" --ensure)"
   ```

   That exports `TROIKA_WORKSPACE`, `TROIKA_PROFILE`, `TROIKA_SCRATCHPAD`,
   `TROIKA_WORKTREES`, and `TROIKA_MEMORY`, reading `<workspace>/.troika/settings.json`
   where the workspace declares them, and creating the three it writes into. It exits
   non-zero when no ancestor of the current directory holds that file — **stop there and
   say so**, and point at `/tr:setup`; a guessed path writes handoff files nobody reads.

2. Read the procedure: `${{CLAUDE_PLUGIN_ROOT}}/skills/{name}/SKILL.md`.
3. Read `$TROIKA_PROFILE` — the workspace profile. Every repo, command, branch, base ref,
   tracker, and URL comes from there; the procedure names none of them, and where the
   profile declares a limit the profile wins.
4. Follow the procedure in order. Every step is a gate: never advance past a failed one, and
   stop on any of its stop conditions rather than working around it.

Roles run with their cwd inside a worktree, so every path from step 1 is used verbatim and
absolute. A relative one writes a file no later role finds.
"""

# The one command that runs *before* there is a workspace, so it cannot open by resolving
# one: step 1 of the shared body would exit non-zero every single time it is used for the
# thing it exists for. It reads its procedure first and creates the workspace from there.
SETUP_BODY = """Run Troika's **{name}** procedure — create a workspace.

**Argument** — `{hint}`: $ARGUMENTS

With no argument, use the current directory, and confirm it with the caller before writing.

This is the one command that runs before a workspace exists, so it does **not** resolve one
first. It creates it.

1. Read the procedure: `${{CLAUDE_PLUGIN_ROOT}}/skills/{name}/SKILL.md`.
2. Follow it in order. It fixes the workspace root, scaffolds `.troika/`, investigates the
   repos, asks only what they cannot answer, and writes the profile.
3. Every step is a gate: never advance past a failed one, and stop on any of its stop
   conditions rather than working around it.

Where a workspace already exists — `.troika/settings.json` or the profile is present — **say so
and ask** what to do: leave it, update it against what the repos now say, or rewrite the
profile from the template. Default to leaving it, and never overwrite what a human wrote
without being asked to in words.

Every other `/tr:*` command resolves that workspace instead of creating one.
"""

# What to do with no argument. Optional for exactly one command, so the two lines are not
# interchangeable: asking for a demo label the profile already declares is a needless
# question, and guessing a ticket key is worse than asking for one.
MISSING_REQUIRED = "\nWith no argument, ask for one and stop — do not guess."
MISSING_OPTIONAL = "\nWith no argument, use the profile's default and say which you used."

# Procedures that must not open by resolving a workspace, keyed by skill.
BODIES = {"workspace-setup": SETUP_BODY}


def command_text(name, alias, hint, desc):
    body = BODIES.get(name, BODY)
    return (
        f"---\nname: {alias}\ndescription: {desc}\nargument-hint: {hint}\n---\n\n"
        + body.format(
            name=name,
            hint=hint,
            missing=MISSING_OPTIONAL if hint.startswith("[") else MISSING_REQUIRED,
        )
    )


MANIFEST = ROOT / ".claude-plugin" / "plugin.json"


def manifest_commands():
    """Claude Code's `commands` key takes command *files*. Pointed at a directory it reads
    that directory as a skill directory instead, which registers every procedure a second
    time — phantom skills, no commands. So the list is spelled out, and generated."""
    return [f"./plugin/commands/{alias}.md" for _, alias, _, _ in skills()]


def sync_manifest():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if payload.get("commands") == manifest_commands():
        return False
    payload["commands"] = manifest_commands()
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return True


def wanted():
    """path -> content, for every file this script owns."""
    out = {}
    for name, alias, hint, desc in skills():
        out[ROOT / "plugin" / "commands" / f"{alias}.md"] = command_text(name, alias, hint, desc)
    return out


def drift():
    """Everything stale, missing, or orphaned. Empty when the surface is current."""
    problems = []
    files = wanted()
    for path, content in files.items():
        rel = path.relative_to(ROOT)
        if not path.exists():
            problems.append(f"{rel}: missing — run python3 plugin/generate.py")
        elif path.read_text(encoding="utf-8") != content:
            problems.append(f"{rel}: stale — run python3 plugin/generate.py")
    # An orphan is the dangerous direction: a command for a skill that no longer exists, or
    # that has been dropped from COMMANDS, still shows up in the `/` menu and sends the
    # model to read a file that may be gone.
    for found in glob.glob(str(ROOT / "plugin" / "commands" / "*.md")):
        if Path(found) not in files:
            problems.append(f"{Path(found).relative_to(ROOT)}: not a command in generate.py's COMMANDS map")
    listed = json.loads(MANIFEST.read_text(encoding="utf-8")).get("commands")
    if listed != manifest_commands():
        problems.append(f"{MANIFEST.relative_to(ROOT)}: commands list is stale — run python3 plugin/generate.py")
    return problems


def main():
    if "--check" in sys.argv:
        problems = drift()
        for p in problems:
            print(f"  {p}")
        return 1 if problems else 0
    for path, content in wanted().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    synced = " and the manifest" if sync_manifest() else ""
    print(f"wrote {len(wanted())} command(s){synced} for {len(skills())} procedure(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

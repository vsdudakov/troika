#!/usr/bin/env python3
"""Generates the slash commands from skills/.

`skills/<name>/SKILL.md` is the procedure itself, in the shape all three hosts discover a
skill in — no wrapper, no second copy. What that shape cannot express is a *command*: an
entry in the `/` menu, with an argument hint, that resolves the workspace before it starts.
So Claude Code and Cursor get `plugin/commands/<name>.md` per procedure, and that file is
the only generated one.

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
# procedures become commands. A `/troika:pr-template` that fills nothing in would be a
# command that cannot be finished.
KIND = "procedure"


def skills():
    """(name, description) for every procedure skill, in filename order."""
    out = []
    for path in sorted(glob.glob(str(ROOT / "skills" / "*" / "SKILL.md"))):
        text = Path(path).read_text(encoding="utf-8")
        kind = re.search(r"\*\*Kind\*\* (\w+)", text)
        if not kind or kind.group(1) != KIND:
            continue
        desc = re.search(r"^description: (.+)$", text, re.M)
        if not desc:
            continue
        out.append((os.path.basename(os.path.dirname(path)), desc.group(1).strip()))
    return out


# What each procedure is invoked *on*. The `/` menu shows this next to the command, so a
# wrong hint sends the caller looking for a ticket key the procedure never reads.
HINTS = {
    "demo-prep": "[demo label]",
    "incident-triage": "<issue link | stack trace | event>",
    "release-cut": "<version>",
    "release-notes": "<version>",
    "ticket-intake": "<request>",
}
DEFAULT_HINT = "<TICKET>"

PREAMBLE = """1. Resolve the workspace, before anything else:

   ```bash
   eval "$(python3 {resolver} --ensure)"
   ```
{note}
   That exports `WS`, `TROIKA_PROFILE`, `TROIKA_HOME`, `TROIKA_SCRATCHPAD`,
   `TROIKA_WORKTREES`, and `TROIKA_MEMORY`, reading `<workspace>/.troika.json` where the
   workspace declares them, and creates the three it writes into. It exits non-zero when there is no workspace above the current
   directory — **stop there and say so**; a guessed path writes handoff files nobody reads.

2. Read the procedure: {procedure}
3. Read `$TROIKA_PROFILE` — the workspace profile. Every repo, command, branch, base ref,
   tracker, and URL comes from there; the procedure names none of them, and where the
   profile declares a limit the profile wins.
4. Follow the procedure in order. Every step is a gate: never advance past a failed one.

Roles run with their cwd inside a worktree, so every path from step 1 is used verbatim and
absolute. A relative one writes a file no later role finds.
"""


def command_text(name, desc):
    procedure = (
        f"`${{CLAUDE_PLUGIN_ROOT}}/skills/{name}/SKILL.md`. If that\n"
        f"   variable is unset, read `$TROIKA_HOME/skills/{name}/SKILL.md` instead."
    )
    return (
        f"---\nname: {name}\ndescription: {desc}\n"
        f"argument-hint: {HINTS.get(name, DEFAULT_HINT)}\n---\n\n"
        f"Run Troika's **{name}** procedure for: $ARGUMENTS\n\n"
        + PREAMBLE.format(
            resolver='"${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py"',
            note="",
            procedure=procedure,
        )
    )


MANIFEST = ROOT / ".claude-plugin" / "plugin.json"


def manifest_commands():
    """Claude Code's `commands` key takes command *files*. Pointed at a directory it reads
    that directory as a skill directory instead, which registers every procedure a second
    time — 13 phantom skills, no commands. So the list is spelled out, and generated."""
    return [f"./plugin/commands/{name}.md" for name, _ in skills()]


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
    for name, desc in skills():
        out[ROOT / "plugin" / "commands" / f"{name}.md"] = command_text(name, desc)
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
    # An orphan is the dangerous direction: a command for a skill that no longer exists
    # still shows up in the `/` menu and sends the model to read a deleted file.
    for found in glob.glob(str(ROOT / "plugin" / "commands" / "*.md")):
        if Path(found) not in files:
            problems.append(f"{Path(found).relative_to(ROOT)}: no matching procedure in skills/")
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

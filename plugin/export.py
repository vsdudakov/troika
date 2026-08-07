#!/usr/bin/env python3
"""Writes the / commands where Codex and Cursor actually look for them.

Claude Code reads `plugin/commands/*.md` from the installed plugin and shows `/tr:<alias>`.
The other two hosts never will: Codex plugins carry no command concept — its slash commands
are the files in `~/.codex/prompts/` — and Cursor does not surface plugin commands, only
skills; its slash commands are the files in `~/.cursor/commands/`. So for those hosts the
commands are exported: the same generated bodies, one file per command, named `tr-<alias>`
because neither directory has namespaces.

Neither host exports `${CLAUDE_PLUGIN_ROOT}`, so the export pins it to a real path — this
checkout by default, or `--root` for an installed marketplace snapshot — and drops the
paragraph that explains how to substitute it, because the export just did. `/tr:` mentions
become `/tr-` so a command never points a caller at a spelling the host cannot complete.

    python3 plugin/export.py codex cursor          # export to both hosts
    python3 plugin/export.py codex --root PATH     # substitute PATH for this checkout

Stale `tr-*.md` files in a target directory are deleted: a command removed from the map
must leave the menu too.
"""

import re
import sys
from pathlib import Path

from generate import command_text, skills

ROOT = Path(__file__).resolve().parent.parent

DESTS = {
    "codex": Path.home() / ".codex" / "prompts",
    "cursor": Path.home() / ".cursor" / "commands",
}

# The two shapes of the substitute-this-variable paragraph in generate.py's bodies. After
# the export substitutes, the instruction would explain a variable that no longer appears.
EXPLAINERS = (
    r" *`\$\{CLAUDE_PLUGIN_ROOT\}` is Claude Code's name.*?variable appears below\.\n\n",
    r" `\$\{CLAUDE_PLUGIN_ROOT\}`\n +is Claude Code's name.*?`skills/` trees\.",
)


def export_text(name, alias, hint, desc, root):
    text = command_text(name, alias, hint, desc)
    for pattern in EXPLAINERS:
        text = re.sub(pattern, "", text, flags=re.S)
    text = text.replace("${CLAUDE_PLUGIN_ROOT}", str(root))
    text = text.replace("/tr:", "/tr-")
    return text.replace(f"---\nname: {alias}\n", f"---\nname: tr-{alias}\n", 1)


def export(host, root):
    dest = DESTS[host]
    dest.mkdir(parents=True, exist_ok=True)
    current = {f"tr-{alias}.md" for _, alias, _, _ in skills()}
    for stale in dest.glob("tr-*.md"):
        if stale.name not in current:
            stale.unlink()
            print(f"removed stale {stale}")
    for name, alias, hint, desc in skills():
        (dest / f"tr-{alias}.md").write_text(
            export_text(name, alias, hint, desc, root), encoding="utf-8"
        )
    print(f"{len(current)} command(s) -> {dest}")


def main(argv):
    root = ROOT
    if "--root" in argv:
        i = argv.index("--root")
        try:
            root = Path(argv[i + 1]).resolve()
        except IndexError:
            raise SystemExit("--root takes a path")
        del argv[i : i + 2]
        if not (root / "skills").is_dir():
            raise SystemExit(f"{root} has no skills/ tree — not a Troika checkout or snapshot")
    hosts = argv or sorted(DESTS)
    unknown = [h for h in hosts if h not in DESTS]
    if unknown:
        raise SystemExit(f"unknown host(s) {', '.join(unknown)}; expected: {', '.join(sorted(DESTS))}")
    for host in hosts:
        export(host, root)


if __name__ == "__main__":
    main(sys.argv[1:])

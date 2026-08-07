#!/usr/bin/env python3
"""Writes the / commands in the shape each non-Claude host can actually invoke.

Claude Code reads `plugin/commands/*.md` from the installed plugin and shows `/tr:<alias>`.
The other two hosts never will, and they differ from each other:

- **Cursor** does not surface plugin commands; its slash commands are the files in
  `~/.cursor/commands/`, flat, named lowercase-with-hyphens. So it gets `/tr-<alias>`.
- **Codex** dropped custom prompts (`~/.codex/prompts/` is no longer read as of 0.147);
  the explicit surface left is skills in `~/.codex/skills/`, mentioned as `$<name>`.
  So it gets a `tr-<alias>/SKILL.md` per command, invoked `$tr-<alias>`.

Neither host exports `${CLAUDE_PLUGIN_ROOT}`, so the export pins it to a real path — this
checkout by default, or `--root` for an installed marketplace snapshot — and drops the
paragraph that explains how to substitute it, because the export just did. `/tr:` mentions
become the host's own spelling, and `$ARGUMENTS` (which only Claude Code substitutes)
becomes a plain instruction to read the argument from the invocation message.

    python3 plugin/export.py codex cursor          # export to both hosts
    python3 plugin/export.py codex --root PATH     # substitute PATH for this checkout

Stale `tr-*` files and directories in a target are deleted: a command removed from the
map must leave the menu too.
"""

import re
import shutil
import sys
from pathlib import Path

from generate import commands

ROOT = Path(__file__).resolve().parent.parent

HOSTS = {
    "codex": (Path.home() / ".codex" / "skills", "$tr-"),
    "cursor": (Path.home() / ".cursor" / "commands", "/tr-"),
}

# The two shapes of the substitute-this-variable paragraph in generate.py's bodies. After
# the export substitutes, the instruction would explain a variable that no longer appears.
EXPLAINERS = (
    r" *`\$\{CLAUDE_PLUGIN_ROOT\}` is Claude Code's name.*?variable appears below\.\n\n",
    r" `\$\{CLAUDE_PLUGIN_ROOT\}`\n +is Claude Code's name.*?`skills/` trees\.",
)


def export_text(alias, text, root, spelling):
    for pattern in EXPLAINERS:
        text = re.sub(pattern, "", text, flags=re.S)
    text = text.replace("${CLAUDE_PLUGIN_ROOT}", str(root))
    text = text.replace("$ARGUMENTS", "whatever follows the command in the caller's message")
    text = text.replace("/tr:", spelling)
    return text.replace(f"---\nname: {alias}\n", f"---\nname: tr-{alias}\n", 1)


def export(host, root):
    dest, spelling = HOSTS[host]
    dest.mkdir(parents=True, exist_ok=True)
    rows = commands()
    current = {f"tr-{alias}" for alias, _ in rows}
    for stale in dest.glob("tr-*"):
        if stale.stem not in current:
            shutil.rmtree(stale) if stale.is_dir() else stale.unlink()
            print(f"removed stale {stale}")
    for alias, text in rows:
        text = export_text(alias, text, root, spelling)
        if host == "codex":
            (dest / f"tr-{alias}").mkdir(exist_ok=True)
            (dest / f"tr-{alias}" / "SKILL.md").write_text(text, encoding="utf-8")
        else:
            (dest / f"tr-{alias}.md").write_text(text, encoding="utf-8")
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
    hosts = argv or sorted(HOSTS)
    unknown = [h for h in hosts if h not in HOSTS]
    if unknown:
        raise SystemExit(f"unknown host(s) {', '.join(unknown)}; expected: {', '.join(sorted(HOSTS))}")
    for host in hosts:
        export(host, root)


if __name__ == "__main__":
    main(sys.argv[1:])

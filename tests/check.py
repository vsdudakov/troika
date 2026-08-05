#!/usr/bin/env python3
"""Structural checks for the agents/ and skills/ trees.

The anchors this tree links into the project profile are a contract
(llm/README.md); so are the file shapes in agents/README.md and skills/README.md.
Nothing here validates prose — only the things that break silently.

    python3 tests/check.py        # exits non-zero on any failure

Companion to run.py: this one asks whether the tree is structurally intact, run.py asks
whether a gate still catches what it claims to. Neither needs a model.
"""

import glob
import os
import re
import sys
from pathlib import Path

# Runnable from anywhere; every path below is relative to the repo root.
os.chdir(Path(__file__).resolve().parent.parent)

FAIL = []


def fail(where, msg):
    FAIL.append(f"{where}: {msg}")


def anchors_of(path):
    """Every fragment a markdown link can resolve to in `path`."""
    text = open(path).read()
    found = set(re.findall(r'<a\s+(?:id|name)="([^"]+)"', text))
    for heading in re.findall(r"^#{1,6}\s+(.+)$", text, re.M):
        found.add(re.sub(r"[^\w\s-]", "", heading).strip().lower().replace(" ", "-"))
    return found


def role_and_skill_files():
    return sorted(glob.glob("agents/*.md") + glob.glob("skills/*.md"))


def body_files():
    return [f for f in role_and_skill_files() if not f.endswith("README.md")]


# --- 1. every link resolves, in-tree and out ---------------------------------

def check_links():
    cache = {}
    for f in role_and_skill_files():
        for _, target in re.findall(r"\[([^\]]*)\]\(([^)]+)\)", open(f).read()):
            if target.startswith(("http", "mailto")):
                continue
            path, _, frag = target.partition("#")
            resolved = os.path.normpath(os.path.join(os.path.dirname(f), path)) if path else f
            if not os.path.exists(resolved):
                # The workspace profile lives outside this repo and is absent in CI.
                if os.path.basename(resolved) == "AGENTS.md":
                    continue
                fail(f, f"dead link {target}")
                continue
            if not frag:
                continue
            if resolved not in cache:
                cache[resolved] = anchors_of(resolved)
            if frag not in cache[resolved]:
                fail(f, f"dead anchor {target}")


# --- 2. profile anchors exist in the template, not just this workspace --------

def check_profile_anchors():
    template = "AGENTS.template.md"
    if not os.path.exists(template):
        fail(template, "missing — the profile contract cannot be verified")
        return
    known = anchors_of(template)
    for f in role_and_skill_files():
        for _, target in re.findall(r"\[([^\]]*)\]\(([^)]+)\)", open(f).read()):
            path, _, frag = target.partition("#")
            if not frag or os.path.basename(path) != "AGENTS.md":
                continue
            if frag not in known:
                fail(f, f"#{frag} is not an anchor in {template}; a fresh workspace reads a dead link")


# --- 3. the nine checks are duplicated by hand in three files ----------------

def check_duplicated_enumerations():
    rules = re.findall(r"^\d+\.\s+\*\*(.+?)\*\*", open("agents/reviewer.md").read(), re.M)
    names = {r.lower() for r in rules}

    inline = {}
    for f in ("skills/internal-review.md", "skills/pr-review.md"):
        m = re.search(r"reviewer › Rules\]\([^)]+\):\s*(.+?)\.$", open(f).read(), re.M)
        if not m:
            fail(f, "no inline copy of the reviewer check list found")
            continue
        inline[f] = [x.strip().lower() for x in m.group(1).split(",")]

    if len(set(map(tuple, inline.values()))) > 1:
        fail("skills/", "internal-review.md and pr-review.md list the reviewer checks differently")

    for f, items in inline.items():
        if len(items) != len(rules):
            fail(f, f"lists {len(items)} reviewer checks; agents/reviewer.md defines {len(rules)}")
        for item in items:
            if not any(item.startswith(n) or n.startswith(item) for n in names):
                fail(f, f"check '{item}' matches no rule name in agents/reviewer.md")

    # the output template must carry one row per rule
    rows = re.findall(r"^- ([A-Z][A-Za-z ]+): <Pass", open("agents/reviewer.md").read(), re.M)
    if len(rows) != len(rules):
        fail("agents/reviewer.md", f"output template has {len(rows)} rows for {len(rules)} rules")
    for row in rows:
        if row.lower() not in names:
            fail("agents/reviewer.md", f"output row '{row}' matches no rule name")


# --- 4. file shapes declared in the two READMEs -----------------------------

AGENT_SECTIONS = ["Scope", "Inputs", "Rules", "Gates", "Output"]


def check_agent_shape():
    for f in sorted(glob.glob("agents/*.md")):
        if f.endswith("README.md"):
            continue
        text = open(f).read()
        body = re.sub(r"```.*?```", "", text, flags=re.S)  # fenced examples are not sections
        sections = re.findall(r"^## (.+)$", body, re.M)
        if sections != AGENT_SECTIONS:
            fail(f, f"sections {sections} != {AGENT_SECTIONS}")
        header = re.findall(r"^- \*\*(Owns|Runs|Model)\*\*", text, re.M)
        if header != ["Owns", "Runs", "Model"]:
            fail(f, f"header list {header} != ['Owns', 'Runs', 'Model']")
        sub = re.findall(r"^  - \*\*([A-Za-z ]+)\*\*", text, re.M)
        if sub[:3] != ["Claude", "Codex", "Why"]:
            fail(f, f"Model sub-bullets start {sub[:3]} != ['Claude', 'Codex', 'Why']")


def check_skill_shape():
    for f in sorted(glob.glob("skills/*.md")):
        if f.endswith("README.md"):
            continue
        text = open(f).read()
        kind = re.search(r"\*\*Kind\*\* (\w+)", text)
        if not kind:
            fail(f, "no **Kind** declared")
        elif kind.group(1) not in ("procedure", "reference", "template"):
            fail(f, f"unknown Kind '{kind.group(1)}'")
        for field in ("Used by", "When", "Ends with"):
            if f"**{field}**" not in text:
                fail(f, f"header line missing **{field}**")


def check_frontmatter():
    for f in body_files():
        m = re.match(r"---\nname: (\S+)\ndescription: (.+)\n", open(f).read())
        if not m:
            fail(f, "frontmatter must open with name: then description:")
            continue
        if m.group(1) != os.path.basename(f)[:-3]:
            fail(f, f"frontmatter name '{m.group(1)}' != filename")


# --- 5. house style ---------------------------------------------------------

def check_style():
    for f in role_and_skill_files():
        for i, line in enumerate(open(f), 1):
            if re.search(r"[^\s]—[^\s]", line):
                fail(f, f"line {i}: em dash needs spaces around it")


def main():
    check_links()
    check_profile_anchors()
    check_duplicated_enumerations()
    check_agent_shape()
    check_skill_shape()
    check_frontmatter()
    check_style()

    if FAIL:
        print(f"{len(FAIL)} problem(s):\n")
        for f in FAIL:
            print(f"  {f}")
        return 1
    print(f"ok — {len(role_and_skill_files())} files, no structural problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())

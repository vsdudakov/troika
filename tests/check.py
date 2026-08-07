#!/usr/bin/env python3
"""Structural checks for the agents/ and skills/ trees, and the plugin surface over them.

The anchors this tree links into the project profile are a contract
(troika/README.md); so are the file shapes in ROLES.md and skills/README.md.
Nothing here validates prose — only the things that break silently.

    python3 tests/check.py        # exits non-zero on any failure

Companion to run.py: this one asks whether the tree is structurally intact, run.py asks
whether a gate still catches what it claims to. Neither needs a model.
"""

import glob
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Runnable from anywhere; every path below is relative to the repo root.
os.chdir(Path(__file__).resolve().parent.parent)

FAIL = []
# These files are read several times over; the tree is small enough to hold all of it.
TEXT = {}
# The contract every role reads the workspace by. The profile lives in the workspace, not
# in this tree and not at any fixed depth from it, so roles cite it by anchor rather than
# link to it — and this file is where those anchors are declared.
TEMPLATE = "PROFILE.template.md"


def fail(where, msg):
    FAIL.append(f"{where}: {msg}")


def text_of(path):
    if path not in TEXT:
        TEXT[path] = Path(path).read_text(encoding="utf-8")
    return TEXT[path]


def links_in(path):
    return re.findall(r"\[([^\]]*)\]\(([^)]+)\)", text_of(path))


def anchors_of(path):
    """Every fragment a markdown link can resolve to in `path`."""
    text = text_of(path)
    found = set(re.findall(r'<a\s+(?:id|name)="([^"]+)"', text))
    for heading in re.findall(r"^#{1,6}\s+(.+)$", text, re.M):
        found.add(re.sub(r"[^\w\s-]", "", heading).strip().lower().replace(" ", "-"))
    return found


def skill_files():
    """One `SKILL.md` per skill directory. The shape is the hosts' — Claude Code, Codex and
    Cursor all discover a skill as a directory with that file in it — and the procedures live
    in it directly rather than behind a wrapper."""
    return sorted(glob.glob("skills/*/SKILL.md"))


def role_and_skill_files():
    # ROLES.md is the roles index, and it sits at the repo root rather than in agents/ for a
    # mechanical reason: a host loads *every* file in agents/ as a role, so an index left in
    # there is offered as a subagent named README.
    return sorted(
        glob.glob("agents/*.md") + ["ROLES.md", "skills/README.md"] + skill_files()
    )


def body_files():
    return [f for f in role_and_skill_files() if not f.endswith(("README.md", "ROLES.md"))]


def skill_name(path):
    """`skills/qa-verify/SKILL.md` -> `qa-verify`."""
    return os.path.basename(os.path.dirname(path))


# --- 1. every link resolves, in-tree and out ---------------------------------

def check_links():
    cache = {}
    for f in role_and_skill_files():
        for _, target in links_in(f):
            if target.startswith(("http", "mailto")):
                continue
            path, _, frag = target.partition("#")
            resolved = os.path.normpath(os.path.join(os.path.dirname(f), path)) if path else f
            if not os.path.exists(resolved):
                fail(f, f"dead link {target}")
                continue
            if not frag:
                continue
            if resolved not in cache:
                cache[resolved] = anchors_of(resolved)
            if frag not in cache[resolved]:
                fail(f, f"dead anchor {target}")


# --- 2. profile anchors exist in the template, not just this workspace --------

# How a role cites the profile: an anchor id alone, in backticks — `#tracker`. Not a link.
# The profile is `<workspace>/.troika/PROFILE.md`, and this tree is usually an installed
# plugin in a host's cache, so no relative link from here can ever reach it; one written
# anyway resolves for nobody and reports nothing when the anchor is wrong.
CITATION = re.compile(r"`(#[a-z][a-z0-9-]*)`")


def check_profile_anchors():
    if not os.path.exists(TEMPLATE):
        fail(TEMPLATE, "missing — the profile contract cannot be verified")
        return
    known = anchors_of(TEMPLATE)
    for f in role_and_skill_files() + plugin_files():
        text = re.sub(r"```.*?```", "", text_of(f), flags=re.S)  # fenced examples are not citations
        for cited in set(CITATION.findall(text)):
            if cited.lstrip("#") not in known:
                fail(f, f"cites {cited}, which is not an anchor in {TEMPLATE}; "
                        "a fresh workspace has nothing under it")
        # A link to the profile cannot resolve from a plugin cache, so the citation form is
        # the only one allowed. This catches the old `../../AGENTS.md#x` shape coming back.
        for _, target in links_in(f):
            if os.path.basename(target.partition("#")[0]) in ("AGENTS.md", "PROFILE.md"):
                fail(f, f"links the profile ({target}); cite the anchor as `#{target.partition('#')[2]}` instead")


# --- 3. the nine checks are duplicated by hand in three files ----------------

def same_check(item, rule):
    """The copies abbreviate — "tests present" for "Tests" — so compare by prefix."""
    return item.startswith(rule) or rule.startswith(item)


def check_sequence(where, items, rules, what):
    """Order is part of the contract, not just membership: a reviewer works down its rule
    list and fills the output rows in the order it reads them, and a copy that reorders
    them silently pairs the wrong evidence with the wrong row."""
    if len(items) != len(rules):
        fail(where, f"{what} has {len(items)} entries; agents/reviewer.md defines {len(rules)}")
        return
    for i, (item, rule) in enumerate(zip(items, rules), 1):
        if not same_check(item, rule):
            fail(where, f"{what} entry {i} is '{item}'; agents/reviewer.md rule {i} is '{rule}'")


def check_duplicated_enumerations():
    reviewer = text_of("agents/reviewer.md")
    rules = [r.lower() for r in re.findall(r"^\d+\.\s+\*\*(.+?)\*\*", reviewer, re.M)]

    inline = {}
    for f in ("skills/internal-review/SKILL.md", "skills/pr-review/SKILL.md"):
        m = re.search(r"reviewer › Rules\]\([^)]+\):\s*(.+?)\.$", text_of(f), re.M)
        if not m:
            fail(f, "no inline copy of the reviewer check list found")
            continue
        inline[f] = [x.strip().lower() for x in m.group(1).split(",")]

    if len(set(map(tuple, inline.values()))) > 1:
        fail("skills/", "internal-review.md and pr-review.md list the reviewer checks differently")

    for f, items in inline.items():
        check_sequence(f, items, rules, "inline check list")

    # the output template must carry one row per rule, in the order the rules are stated
    rows = [r.lower() for r in re.findall(r"^- ([A-Z][A-Za-z ]+): <Pass", reviewer, re.M)]
    check_sequence("agents/reviewer.md", rows, rules, "output template")


# --- 4. file shapes declared in the two READMEs -----------------------------

AGENT_SECTIONS = ["Scope", "Inputs", "Rules", "Gates", "Output"]
# A role declares what its row *needs* and why; the model ids and efforts themselves are the
# workspace's, in PROFILE.md › Models and effort (`#models`). A sub-bullet naming a host —
# `Claude`, `Codex` — is the hardcoded shape coming back, so it fails as an undeclared one.
MODEL_SUBS = ["Needs", "Why"]
MODEL_SUBS_OPTIONAL = ["Raise it when", "Drop it when", "Also"]


def check_agent_shape():
    for f in sorted(glob.glob("agents/*.md")):
        text = text_of(f)
        body = re.sub(r"```.*?```", "", text, flags=re.S)  # fenced examples are not sections
        sections = re.findall(r"^## (.+)$", body, re.M)
        if sections != AGENT_SECTIONS:
            fail(f, f"sections {sections} != {AGENT_SECTIONS}")
        header = re.findall(r"^- \*\*(Owns|Runs|Model)\*\*", text, re.M)
        if header != ["Owns", "Runs", "Model"]:
            fail(f, f"header list {header} != ['Owns', 'Runs', 'Model']")
        # Only the bullets nested under **Model**, not every two-space bullet in the file:
        # a nested list anywhere else is legal prose, and reporting it as a Model sub-bullet
        # would fail the build with the wrong reason.
        block = re.search(r"^- \*\*Model\*\*.*?(?=^\S|\Z)", text, re.M | re.S)
        sub = re.findall(r"^  - \*\*([A-Za-z ]+)\*\*", block.group(0) if block else "", re.M)
        n = len(MODEL_SUBS)
        if sub[:n] != MODEL_SUBS:
            fail(f, f"Model sub-bullets start {sub[:n]} != {MODEL_SUBS}")
        # An undeclared sub-bullet is drift the README does not describe.
        for extra in [s for s in sub[n:] if s not in MODEL_SUBS_OPTIONAL]:
            fail(f, f"Model sub-bullet '{extra}' is not one of {MODEL_SUBS_OPTIONAL}")


def check_skill_shape():
    for f in skill_files():
        text = text_of(f)
        kind = re.search(r"\*\*Kind\*\* (\w+)", text)
        if not kind:
            fail(f, "no **Kind** declared")
        elif kind.group(1) not in ("procedure", "reference", "template"):
            fail(f, f"unknown Kind '{kind.group(1)}'")
        for field in ("Used by", "When", "Ends with"):
            if f"**{field}**" not in text:
                fail(f, f"header line missing **{field}**")


def check_stop_conditions():
    """A procedure that cannot say when to stop will improvise past a failed gate. Every
    one declares them; references and templates are read *by* a procedure and have none."""
    for f in skill_files():
        kind = re.search(r"\*\*Kind\*\* (\w+)", text_of(f))
        has = re.search(r"^## Stop conditions", text_of(f), re.M)
        if kind and kind.group(1) == "procedure" and not has:
            fail(f, "a procedure with no '## Stop conditions' section")
        if kind and kind.group(1) != "procedure" and has:
            fail(f, f"a {kind.group(1)} declares stop conditions; only a procedure runs and can stop")


def check_template_anchor_table():
    """The template is two lists of the same anchors — the contract table at the top and the
    skeleton below it — and they drift silently. An anchor in the skeleton but not the table
    is one no role is told exists; one in the table but not the skeleton is a heading a fresh
    workspace never gets, so every citation of it reads a section that was never written."""
    if not os.path.exists(TEMPLATE):
        return
    text = text_of(TEMPLATE)
    table = set(re.findall(r"^\| `#([a-z][a-z0-9-]*)`", text, re.M))
    skeleton = set(re.findall(r'<a id="([a-z][a-z0-9-]*)"></a>', text))
    for missing in sorted(skeleton - table):
        fail(TEMPLATE, f"#{missing} is in the skeleton but not in the anchor table")
    for missing in sorted(table - skeleton):
        fail(TEMPLATE, f"#{missing} is in the anchor table but not in the skeleton")


def check_fixture_profile():
    """The behavioural fixtures answer to the same contract as a real workspace. An anchor
    the template declares but the fixture lacks makes every case run against a profile that
    is thinner than the one the roles were written for."""
    fixture = "tests/fixtures/PROFILE.md"
    if not (os.path.exists(TEMPLATE) and os.path.exists(fixture)):
        return
    declared = set(re.findall(r'<a id="([a-z][a-z0-9-]*)"></a>', text_of(TEMPLATE)))
    present = set(re.findall(r'<a id="([a-z][a-z0-9-]*)"></a>', text_of(fixture)))
    for missing in sorted(declared - present):
        fail(fixture, f"lacks #{missing}, which {TEMPLATE} declares — cases run on a thinner profile")


def check_cases():
    """Each behavioural case is a directory with an expect.yaml naming a role and a skill
    that exist. A case pointing at a renamed skill fails at run time, an hour and a model
    call later; here it costs nothing."""
    for spec in sorted(glob.glob("tests/cases/*/expect.yaml")):
        text = text_of(spec)
        role = re.search(r"^role: (\S+)", text, re.M)
        skill = re.search(r"^skill: (\S+)", text, re.M)
        if not role or not skill:
            fail(spec, "must declare both role: and skill:")
            continue
        if not os.path.exists(f"agents/{role.group(1)}.md"):
            fail(spec, f"role '{role.group(1)}' has no file in agents/")
        if not os.path.exists(f"skills/{skill.group(1)}/SKILL.md"):
            fail(spec, f"skill '{skill.group(1)}' has no SKILL.md")
        if "why:" not in text:
            fail(spec, "no why: — a case nobody can read is a case nobody can fix")
    for case in sorted(glob.glob("tests/cases/*")):
        if os.path.basename(case) == "_base" or not os.path.isdir(case):
            continue
        if not os.path.exists(f"{case}/expect.yaml"):
            fail(case, "case directory with no expect.yaml")


def check_command_flags():
    """generate.py's FLAGS map documents a procedure's flags in the `/` menu. A key that is
    not a commanded skill documents a flag on a command that does not exist."""
    module = load_module("plugin/generate.py", "generate_flags")
    if module is None:
        return
    commanded = set(module.COMMANDS)
    for name in getattr(module, "FLAGS", {}):
        if name not in commanded:
            fail("plugin/generate.py", f"FLAGS names '{name}', which has no command")


def check_frontmatter():
    for f in body_files():
        m = re.match(r"---\nname: (\S+)\ndescription: (.+)\n", text_of(f))
        if not m:
            fail(f, "frontmatter must open with name: then description:")
            continue
        expected = skill_name(f) if f.endswith("SKILL.md") else os.path.basename(f)[:-3]
        if m.group(1) != expected:
            fail(f, f"frontmatter name '{m.group(1)}' != {expected}")


# --- 5. the plugin surface ---------------------------------------------------

CLAUDE_MANIFEST = ".claude-plugin/plugin.json"
CLAUDE_MARKETPLACE = ".claude-plugin/marketplace.json"
CODEX_MANIFEST = ".codex-plugin/plugin.json"
CODEX_MARKETPLACE = ".agents/plugins/marketplace.json"


def plugin_files():
    return sorted(glob.glob("plugin/commands/*.md"))


def load_json(path):
    if not os.path.exists(path):
        fail(path, "missing — the plugin cannot be installed without it")
        return None
    try:
        return json.loads(text_of(path))
    except json.JSONDecodeError as e:
        fail(path, f"invalid JSON: {e}")
        return None


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail(path, "missing — the plugin surface cannot be verified")
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_tracked():
    """A file this tree links to but git ignores exists for you and for nobody else.
    An unanchored `memory/` in .gitignore matches `skills/memory/` too, and the skill is
    silently never committed — which reads as a dead link in CI and nowhere else."""
    files = role_and_skill_files() + plugin_files()
    try:
        proc = subprocess.run(
            ["git", "check-ignore", "--stdin"],
            input="\n".join(files), capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return  # no git, or no repository: nothing to verify against
    if proc.returncode not in (0, 1):
        return
    for line in proc.stdout.splitlines():
        fail(line.strip(), "ignored by .gitignore — it will be missing for everyone else")


def check_resolved_paths():
    """No role may spell a workspace path out. `$TROIKA_WORKSPACE/.troika/scratchpad` is a path
    the workspace is allowed to move, so a literal one silently ignores where it moved to."""
    for f in role_and_skill_files() + plugin_files():
        for i, line in enumerate(text_of(f).splitlines(), 1):
            if re.search(r"\$TROIKA_WORKSPACE/(\.troika|SETUP\.md|AGENTS\.md|troika\b)", line):
                fail(f, f"line {i}: hardcoded path — use $TROIKA_SCRATCHPAD, "
                        "$TROIKA_WORKTREES, $TROIKA_MEMORY, or $TROIKA_PROFILE")


def check_resolver():
    """The resolver is the one piece of this tree that runs before a model reads anything,
    so it is checked by running it — against a workspace built for the purpose."""
    resolve = load_module("plugin/resolve.py", "resolve")
    if resolve is None:
        return
    with tempfile.TemporaryDirectory() as tmp:
        # .resolve(): on macOS the temp directory is reached through a symlink, and the
        # resolver reports real paths — comparing against the symlinked one fails for a
        # reason that has nothing to do with the code under test.
        root = Path(tmp).resolve()
        # --init is how every workspace is created, so it is what the rest is tested on.
        resolve.init(str(root))
        for path in (".troika/settings.json", ".troika/.gitignore", ".troika/scratchpad",
                     ".troika/worktrees", ".troika/memory"):
            if not (root / path).exists():
                fail("plugin/resolve.py", f"--init did not create {path}")
        elsewhere = root / "elsewhere" / "sp"
        config = root / resolve.CONFIG
        payload = json.loads(config.read_text(encoding="utf-8"))
        payload["scratchpad"] = str(elsewhere)
        del payload["worktrees"]
        config.write_text(json.dumps(payload), encoding="utf-8")
        deep = root / "repo" / "pkg" / "sub"
        deep.mkdir(parents=True)
        try:
            out = resolve.resolve(str(deep))
        except SystemExit as e:
            fail("plugin/resolve.py", f"failed on a valid workspace: {e}")
            return
        if out.get("TROIKA_WORKSPACE") != str(root):
            fail("plugin/resolve.py", f"resolved TROIKA_WORKSPACE {out.get('TROIKA_WORKSPACE')!r} from a subdirectory, not the root")
        # An absolute override must survive verbatim; a declared path silently re-anchored
        # under the workspace is the failure this whole mechanism exists to prevent.
        if out.get("TROIKA_SCRATCHPAD") != str(elsewhere):
            fail("plugin/resolve.py", "an absolute scratchpad in settings.json was not honoured")
        # A key deleted by hand falls back rather than failing the run.
        if out.get("TROIKA_WORKTREES") != str(root / ".troika" / "worktrees"):
            fail("plugin/resolve.py", "an undeclared path did not fall back to the .troika/ layout")
        if out.get("TROIKA_PROFILE") != str(root / ".troika" / "PROFILE.md"):
            fail("plugin/resolve.py", "the profile did not resolve to .troika/PROFILE.md")
        # settings.json is the only marker. A repo's own AGENTS.md must not be taken for a
        # workspace: stopping there would scatter handoff files through a worktree. The env
        # fallback below is real behaviour, so the negative test runs with it cleared.
        saved = os.environ.pop("TROIKA_WORKSPACE", None)
        try:
            with tempfile.TemporaryDirectory() as other:
                stray = Path(other).resolve()
                (stray / "AGENTS.md").write_text("not a workspace", encoding="utf-8")
                (stray / "repo").mkdir()
                try:
                    found = resolve.resolve(str(stray / "repo")).get("TROIKA_WORKSPACE")
                    fail("plugin/resolve.py", f"resolved {found!r} with no settings.json anywhere above it")
                except SystemExit as e:
                    if "tr:setup" not in str(e):
                        fail("plugin/resolve.py", f"the no-workspace error does not point at setup: {e}")
                # An absolute `worktrees` override puts a role's cwd outside the workspace;
                # the exported TROIKA_WORKSPACE is the way back to it.
                os.environ["TROIKA_WORKSPACE"] = str(root)
                try:
                    if resolve.resolve(str(stray / "repo")).get("TROIKA_WORKSPACE") != str(root):
                        fail("plugin/resolve.py", "the TROIKA_WORKSPACE fallback did not resolve the exported workspace")
                except SystemExit as e:
                    fail("plugin/resolve.py", f"failed from an external worktree despite TROIKA_WORKSPACE being set: {e}")
        finally:
            if saved is None:
                os.environ.pop("TROIKA_WORKSPACE", None)
            else:
                os.environ["TROIKA_WORKSPACE"] = saved


def check_plugin_wrappers():
    """The wrappers are generated. Hand-editing one is how a command and the procedure it
    names drift apart, so the check is regeneration, not inspection."""
    module = load_module("plugin/generate.py", "generate")
    if module is None:
        return
    # drift() reads every SKILL.md and manifest; one malformed file must land in FAIL with
    # the rest of the report, not abort the run before the checks below it.
    try:
        problems = module.drift()
    except (Exception, SystemExit) as e:
        fail("plugin/", f"generate.py drift() failed: {e}")
        return
    for problem in problems:
        fail("plugin/", problem)


def check_versions():
    """VERSION is the source; every manifest is written from it by plugin/version.py.
    A host keys an installed plugin on name *and* version, so two manifests that disagree
    install as two plugins from one tree and only one of them is ever updated."""
    module = load_module("plugin/version.py", "version")
    if module is None:
        return
    try:
        problems = module.drift()
    except (Exception, SystemExit) as e:
        fail("VERSION", f"version.py drift() failed: {e}")
        return
    for problem in problems:
        fail("VERSION", problem)


def check_manifests():
    claude = load_json(CLAUDE_MANIFEST)
    codex = load_json(CODEX_MANIFEST)
    market = load_json(CLAUDE_MARKETPLACE)
    load_json(CODEX_MARKETPLACE)

    if claude and codex and claude.get("name") != codex.get("name"):
        fail(CODEX_MANIFEST, f"name {codex.get('name')!r} != {claude.get('name')!r} in {CLAUDE_MANIFEST}")

    if claude and market:
        entries = {p.get("name"): p for p in market.get("plugins", [])}
        if claude.get("name") not in entries:
            fail(CLAUDE_MARKETPLACE, f"no entry named {claude.get('name')!r}")

    if not claude:
        return

    # Claude Code auto-loads agents/ and offers every file in it as a subagent, so anything
    # in there that is not a role becomes one. An explicit list would be the alternative, but
    # a listed path currently registers nothing — the directory has to be clean instead.
    if "agents" in claude:
        fail(CLAUDE_MANIFEST, "drop the agents key: a listed agent path registers nothing, "
                              "and setting it disables the agents/ scan that does work")
    # Nothing else guards the directory's contents, because nothing else has to:
    # check_agent_shape() demands the five role sections of every file in agents/, so a
    # stray note or index in there fails there first.

    # `commands` takes command *files*; a directory there is read as a skill directory, which
    # silently registers every procedure a second time.
    for path in claude.get("commands", []):
        if os.path.isdir(path.removeprefix("./")):
            fail(CLAUDE_MANIFEST, f"commands lists the directory {path}; list the files in it")
    skills = codex.get("skills") if codex else None
    if skills and not os.path.isdir(skills.removeprefix("./")):
        fail(CODEX_MANIFEST, f"skills points at {skills}, which is not a directory")


# --- 6. house style ---------------------------------------------------------

def check_style():
    for f in role_and_skill_files() + plugin_files():
        for i, line in enumerate(text_of(f).splitlines(), 1):
            if re.search(r"[^\s]—[^\s]", line):
                fail(f, f"line {i}: em dash needs spaces around it")


def main():
    check_links()
    check_profile_anchors()
    check_duplicated_enumerations()
    check_agent_shape()
    check_skill_shape()
    check_stop_conditions()
    check_template_anchor_table()
    check_fixture_profile()
    check_cases()
    check_command_flags()
    check_frontmatter()
    check_plugin_wrappers()
    check_manifests()
    check_versions()
    check_resolver()
    check_resolved_paths()
    check_tracked()
    check_style()

    if FAIL:
        print(f"{len(FAIL)} problem(s):\n")
        for f in FAIL:
            print(f"  {f}")
        return 1
    print(
        f"ok — {len(role_and_skill_files())} files "
        f"+ {len(plugin_files())} commands, no structural problems"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

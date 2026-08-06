.PHONY: help repo-seo check test test-check test-dry cov commands version dist release install install-release upgrade uninstall docs docs-install docs-serve clean

# Troika is markdown plus two Python scripts on the stdlib, so there is nothing
# to build and nothing to install for the gates — `make check` runs on a bare
# python3. Only the docs need a virtualenv.

VENV ?= .venv
PY := $(VENV)/bin/python
RUNS ?= 5
CASE ?=
# The agent command the behavioural suite drives. Must read a prompt on stdin
# and write the reply to stdout.
AGENT ?= claude -p --model claude-fable-5 --effort high

help:
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

# --- Gates -------------------------------------------------------------------

check: ## Structural gate: links, anchors, file shapes, commands, resolver (no model)
	python3 tests/check.py

test-check: ## Validate the behavioural fixtures without spending anything
	python3 tests/run.py --check

test-dry: ## Print the exact prompt a case sends to the agent (CASE=n-plus-one)
	python3 tests/run.py --dry-run $(if $(CASE),--case $(CASE),)

test: ## Behavioural gate: real model runs, catch rate per case (RUNS=5, CASE=…)
	TROIKA_CMD="$(AGENT)" python3 tests/run.py --runs $(RUNS) $(if $(CASE),--case $(CASE),)

# Everything CI runs, in the order CI runs it.
cov: check test-check ## Both no-spend gates, as CI runs them

# --- Plugin surface ----------------------------------------------------------

commands: ## Regenerate the / commands and the manifest list from skills/
	python3 plugin/generate.py

install: commands check ## Install into Claude Code (project scope) and Codex
	claude plugin marketplace add $(PWD) || claude plugin marketplace update troika
	claude plugin install troika@troika --scope project
	codex plugin marketplace add $(PWD) || true
	codex plugin add troika@troika

# A host installs from a cached marketplace snapshot, so refreshing the marketplace
# and updating the plugin are two steps everywhere. Only the first one sees a new
# release; skipping it re-installs the version already on disk. A pinned ref still
# resolves to that ref — bump the pin first (docs/reference/releases.md).
upgrade: ## Refresh the marketplace and update the plugin in Claude Code, Codex and Cursor
	-claude plugin marketplace update troika
	-claude plugin update troika@troika
	-codex plugin marketplace upgrade
	-codex plugin add troika@troika
	-cursor-agent plugin marketplace update https://github.com/vsdudakov/troika
	@echo "restart the host to load the new version"

uninstall: ## Remove the plugin from both hosts
	-claude plugin uninstall troika@troika --scope project
	-claude plugin marketplace remove troika
	-codex plugin remove troika
	-codex plugin marketplace remove troika

# --- Repository metadata (discoverability) -----------------------------------
# GitHub's own search, and every crawler that reads the repo page, index the
# description and topics — they are not cosmetic. Re-run after renaming or
# repositioning the project.

repo-seo: ## Push the description, homepage and topics to GitHub
	gh repo edit vsdudakov/troika \
	  --description "Turn a tracker ticket into a reviewed, QA-verified pull request. An AI coding-agent pipeline for full-stack developers — plugin for Claude Code, Codex and Cursor." \
	  --homepage "https://vsdudakov.github.io/troika/" \
	  --enable-issues --enable-wiki=false
	gh repo edit vsdudakov/troika \
	  --add-topic ai-agents --add-topic agentic-workflow --add-topic coding-agent \
	  --add-topic claude-code --add-topic claude-code-plugin --add-topic codex \
	  --add-topic cursor --add-topic llm --add-topic developer-tools \
	  --add-topic code-review --add-topic automated-code-review --add-topic qa-automation \
	  --add-topic release-automation --add-topic pull-request --add-topic devtools \
	  --add-topic git-worktree --add-topic software-development --add-topic automation \
	  --add-topic agents --add-topic prompt-engineering

# --- Releases ----------------------------------------------------------------
# VERSION is the single source; plugin/version.py writes it into all four
# manifests and tests/check.py fails if any of them drifts.

version: ## Set the version everywhere (make version V=0.2.0), or print it
	@python3 plugin/version.py $(V)
	@[ -z "$(V)" ] || $(MAKE) --no-print-directory check

dist: check ## Build the release archive locally, exactly as CI does
	@v=$$(cat VERSION); \
	git archive --format=tar.gz --prefix="troika-$$v/" -o "troika-$$v.tar.gz" HEAD \
	  .claude-plugin .codex-plugin .cursor-plugin .agents agents skills plugin \
	  AGENTS.template.md ROLES.md README.md LICENSE.md VERSION; \
	shasum -a 256 "troika-$$v.tar.gz" | tee "troika-$$v.tar.gz.sha256"

# Tag and push; .github/workflows/release.yml re-runs the gates on the tag,
# builds the archive and publishes the GitHub Release.
release: check test-check ## Tag the current VERSION and push it (triggers the release workflow)
	@v=$$(cat VERSION); \
	git diff --quiet || { echo "working tree is dirty — commit first"; exit 1; }; \
	git tag -a "v$$v" -m "troika v$$v"; \
	git push origin "v$$v"; \
	echo "pushed v$$v — watch: gh run watch"

install-release: ## Install a published release (make install-release V=0.2.0)
	@[ -n "$(V)" ] || { echo "usage: make install-release V=0.2.0"; exit 1; }
	mkdir -p $(HOME)/.troika
	curl -fsSL "https://github.com/vsdudakov/troika/releases/download/v$(V)/troika-$(V).tar.gz" \
	  | tar xz -C $(HOME)/.troika
	claude plugin marketplace add $(HOME)/.troika/troika-$(V) || true
	claude plugin install troika@troika
	codex plugin marketplace add $(HOME)/.troika/troika-$(V) || true
	codex plugin add troika@troika

# --- Documentation (MkDocs Material) -----------------------------------------

docs-install: ## Create .venv and install the docs toolchain
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -U pip -r docs/requirements.txt

docs: ## Build the static site into ./site (social cards on, like CI)
	CI=true $(PY) -m mkdocs build --strict

docs-serve: ## Live-preview the docs at http://127.0.0.1:8000
	$(PY) -m mkdocs serve

clean: ## Remove build artefacts (never touches scratchpad/ or worktrees/)
	rm -rf site .cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

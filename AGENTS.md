# AGENTS.md — AI coding agent instructions

Purpose: give AI coding agents the minimal, high-value context they need to work productively in this repository. Link to detailed docs instead of copying them.

## Quick actions

- **Run tests:** `pytest -q` (requires `pytest`).
- **Install editable package:** `python -m pip install -e .` (project uses `setup.cfg`).
- **Preview docs locally:** `python -m http.server --directory docs 8000` then open [http://localhost:8000](http://localhost:8000)

## Key locations

- Repo root: [README.md](README.md) — high-level project overview and links.
- Docs site: [docs/](docs/README.md) — GitHub Pages site and client-readiness tools.
- Helper agents: [helper/README.md](helper/README.md) and [helper/client_readiness_agent.py](helper/client_readiness_agent.py).
- Case notes: [cases/](cases/README.md) — short, public-safe examples and patterns.
- Tests: [tests/test_client_readiness_agent.py](tests/test_client_readiness_agent.py).
- Entrypoint scripts: `bin/gitmcamner` (CLI launcher).

## Conventions & expectations for agents

- Link, don't duplicate: prefer linking to existing docs instead of copying content.
- Local-first: prefer running tools against local files and the `docs/` site when reproducing behavior.
- Human-reviewed automation: propose actions as PRs or patches; do not push or merge changes without review.
- Minimal edits: apply small, focused changes; follow repository scripts (`release.sh`, `install-gitmcamner.sh`) for release workflows.

## Useful commands for contributors

- Run unit tests: `pytest -q`
- Serve the docs: `python -m http.server --directory docs 8000`
- Run the helper agent locally: `python helper/client_readiness_agent.py`

## When to ask the human

- If a change affects release, CI, or publishing (files: `release.sh`, `.github/workflows/`), ask before modifying.
- If a change requires external credentials or system-level access, stop and request guidance.

---

If you want, I can also add a dedicated `.github/copilot-instructions.md` with brief CI and contribution rules, or create a small `skill` file for automating common repo tasks. Which would you prefer next?

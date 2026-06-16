# Mattias Camner

Infrastructure architect building practical systems for endpoint readiness,
Zero Trust operations, client validation, and terminal-native automation.

```text
complex enterprise environment -> clear signals -> repeatable action
```

[![Pages](https://img.shields.io/badge/pages-live-174c5a)](https://mcamner.github.io/MCamner/)
[![Focus](https://img.shields.io/badge/focus-EUC%20%7C%20Zero%20Trust%20%7C%20Automation-orange)](#what-i-build)
[![Status](https://img.shields.io/badge/status-active-success)](#demo-flow)

I work where infrastructure, security, endpoint platforms, and operations meet:
Citrix, IGEL OS, eLux, Intune, identity, certificates, client health, and the
messy last mile where systems either work for users or quietly fail.

## Portfolio snapshot

* Endpoint readiness: Citrix, IGEL OS, eLux, Intune, certificates, and client health
* Local-first automation: terminal workflows, release gates, and repo scoring
* AI governance: MCP tools, safety classes, contracts, and reviewed actions
* Architecture style: practical systems, visible state, and repeatable operations

---

## In short

I build practical architecture systems that connect infrastructure, automation,
endpoint management, and local AI into controlled, reviewable workflows.

The common thread is governance: local-first tools, explicit safety boundaries,
repeatable checks, and enough structure that an operator can understand what
will happen before anything changes.

The MQ stack is the core of that work: a set of repos that take a local git repo,
endpoint workflow, or operational screenshot and turn it into scored health
signals, release gates, regression alerts, contract checks, CI-enforced stack
checks, and structured reviews.

```text
infrastructure / endpoint / repo -> structured signal -> reviewed action
```

---

## Portfolio Map

### Architecture & Infrastructure

* [zephyr-workbench](https://github.com/MCamner/zephyr-workbench)
* [MCamner](https://github.com/MCamner/MCamner)

Executable architecture, validation, and system maps.

### Local AI / Agent Runtime

* [mq-mcp](https://github.com/MCamner/mq-mcp)
* [mq-agent](https://github.com/MCamner/mq-agent)
* [mq-hal](https://github.com/MCamner/mq-hal)
* [atlas-one](https://github.com/MCamner/atlas-one)

Controlled tool execution, orchestration, and local-first AI workflows.

### Enterprise Endpoint Automation

* [mq-ums](https://github.com/MCamner/mq-ums)
* [Design-Prototype](https://github.com/MCamner/Design-Prototype)

IGEL, Citrix, client readiness, and allowlisted operations.

### Repo Intelligence & Quality Gates

* [repo-signal](https://github.com/MCamner/repo-signal)
* [mq-image-analyze](https://github.com/MCamner/mq-image-analyze)

Readiness scoring, release gates, and visual review inputs.

### Writing / Knowledge Systems

* [mcamner-journal](https://github.com/MCamner/mcamner-journal)
* [atlas-loop](https://github.com/MCamner/atlas-loop)

Reusable prompts, notes, and publishing workflows.

---

## Core Portfolio Repos

These are the six repos that best describe the architecture story:

* MCamner — portfolio and case surface
* mq-mcp — deterministic MCP runtime
* mq-agent — terminal agent orchestrator
* repo-signal — repo readiness engine
* mq-ums — IGEL UMS operator UI
* zephyr-workbench — architecture workbench

---

## Trust Signals

* local-first execution by default
* explicit safety classes and allowlisted actions
* release gates, readiness scoring, and regression checks
* GitHub Pages demos where a visual surface helps
* MIT licensing on the main portfolio repos where reuse is intended
* documented boundaries between runtime, orchestration, and operators

---

## MQ Ecosystem Map

The MQ projects are a local-first toolchain for turning operational complexity
into visible state, safer decisions, and repeatable action.

```text
mqlaunch (macos-scripts)
    └──▶ mq-agent
              ├──▶ stack sweep ──▶ repo-signal
              │         └──▶ ~/.mq-agent/sweep-history.jsonl
              ├──▶ stack history / alert / report
              ├──▶ release-check / release-notes / contract-check
              ├──▶ CI gate ──▶ GitHub Actions
              │         └──▶ contract-check + release-check
              └──▶ deep review ──▶ mq-mcp (tool runtime)
                                        ├──▶ repo-signal
                                        ├──▶ mq-image-analyze
                                        └──▶ mq-hal / mq-ums
```

### Current MQ Stack Repos

* [macos-scripts](https://github.com/MCamner/macos-scripts)
  Terminal entrypoint for `mqlaunch` menus, stack cockpit, and workflow chains.
  Version: `v1.0.0`. Status: B2 Stack Cockpit; menu item 18 runs the full
  stack sweep pipeline.
* [mq-agent](https://github.com/MCamner/mq-agent)
  Orchestrator for stack sweeps, health history, regression alerts, release
  gates, release notes, contract gate, CI gate, and code review.
  Version: `v1.11.0`. Status: stack contract gate live; CI now runs
  `contract-check` and `release-check` on PRs and `main`.
* [mq-mcp](https://github.com/MCamner/mq-mcp)
  Deterministic tool runtime with safety classes, contracts, and 95+
  documented tools.
  Version: `v1.11.0`. Status: learning contract layer and strong contract
  governance across the stack.
* [repo-signal](https://github.com/MCamner/repo-signal)
  Repo intelligence for README quality, publish readiness, and AI context
  exports.
  Version: `v1.4.0`. Status: stable scoring engine that powers
  `mq-agent stack sweep` per-repo scores.
* [mq-image-analyze](https://github.com/MCamner/mq-image-analyze)
  Visual perception for OCR, diagrams, screenshots, and architecture review.
  Version: `v1.4.0`. Status: `image_ocr` MCP tool integrated into the
  `mq-agent` review flow.
* [mq-hal](https://github.com/MCamner/mq-hal)
  Operator layer for safe natural-language command routing.
  Version: `v1.2.0`. Status: vector-store health and stack status checks.
* [mq-ums](https://github.com/MCamner/mq-ums)
  Browser UI for IGEL UMS operations through allowlisted PowerShell.
  Version: `v0.1.4`. Status: operator surface validated against live UMS.
* [atlas-one](https://github.com/MCamner/atlas-one)
  Prompt routing studio for structured reasoning and reusable AI workflows.
  Version: `v1.4.0`. Status: MQ ecosystem integration and personal workflow
  packs.

Together, these repos describe one operating pattern:

```text
local repo / endpoint / screenshot -> structured signal -> reviewed action
```

---

## Demo Flow

From one terminal, the full MQ stack health pipeline — no API key, no network calls:

```bash
# Score every repo in the MQ stack
mq-agent stack sweep

# Consolidated view: score, trend, alert, ready per repo
mq-agent stack report

# Regression gate: exits 1 if any repo dropped ≥ 10 pts or fell below 80
mq-agent stack alert

# Release gate: exits 1 if any repo has blockers (VERSION, CHANGELOG, clean tree)
mq-agent stack release-check

# Draft release notes from git commits since last tag, per repo
mq-agent stack release-notes

# Contract gate: exits 1 if repo contracts are missing, blocked, or drifting
mq-agent stack contract-check
```

CI-enforced stack gate:

```text
pull request / push to main
  -> GitHub Actions
  -> mq-agent stack contract-check --json
  -> mq-agent stack release-check --json
```

Or trigger from the terminal menu (macOS):

```bash
mqlaunch
# → Agent menu → 18. MQ Stack cockpit
```

Deep per-repo review (requires OpenAI API key and mq-mcp running):

```bash
mq-agent signal . --brain        # repo-signal readiness + brain note
mq-agent review repo . --brain   # mq-mcp code review + brain note
mq-agent release-check --dry-run # release gate preview
```

Full signal flow:

```text
terminal (mqlaunch)
  └──▶ mq-agent stack sweep
            ├──▶ repo-signal scores each repo (local, no key)
            └──▶ history written to JSONL
                (~/.mq-agent/sweep-history.jsonl)
  └──▶ mq-agent stack alert
      compare the last two sweeps
  └──▶ mq-agent stack report
      score + trend + alert + ready per repo
  └──▶ mq-agent stack release-check
      VERSION, CHANGELOG, branch, clean tree
  └──▶ mq-agent stack release-notes
      commits since last tag, per repo
  └──▶ mq-agent stack contract-check
      .mq/repo-contract.json + VERSION sync
  └──▶ GitHub Actions MQ Stack Gate
      CI-enforced contract + release checks
```

History persists across runs — trend and regression data accumulates automatically.

---

## What This Repo Is

This repository powers the `mcamner.github.io/MCamner` GitHub Pages site and a
set of browser-based client readiness tools under `docs/`.

It is both:

* a technical profile for my systems and automation work
* a working static toolkit for endpoint readiness and validation demos

Live site:

```text
https://mcamner.github.io/MCamner/
```

---

## Quick Start

Run the static site locally:

```bash
python3 -m http.server 8000 --directory docs
```

Open:

```text
http://127.0.0.1:8000/
```

Run the primary client readiness helper:

```bash
python3 helper/client_readiness_agent.py --baseline igel-os12
```

Generate saved v2 diagnostic data:

```bash
python3 helper/client_readiness_agent_v2.py \
  --profile igel-os12-citrix \
  --pretty \
  --out docs/live-client-data.json
```

Run local checks:

```bash
python3 -m compileall helper tests
python3 -m pytest tests
python3 -m flake8 helper tests
```

---

## Featured Tool: Client Readiness Diagnostics

A browser-first readiness surface for enterprise clients. It validates signals
that matter before a user hits a broken Citrix, kiosk, browser, certificate, or
network path.

```text
client state -> readiness profile -> pass/fail signals -> support-ready report
```

Public entrypoints:

* [`docs/index.html`](docs/index.html) - landing page for the client tools
* [`docs/client-readiness-check.html`](docs/client-readiness-check.html)
  v1 browser readiness check.
* [`docs/client-readiness-v2.html`](docs/client-readiness-v2.html)
  multi-profile diagnostics.

Helper entrypoints:

* [`helper/client_readiness_agent.py`](helper/client_readiness_agent.py)
  local read-only helper API.
* [`helper/client_readiness_agent_v2.py`](helper/client_readiness_agent_v2.py)
  v2 data collector.
* [`helper/client_helper.py`](helper/client_helper.py)
  experimental helper surface.

The v2 page reads data in this order:

```text
localhost helper -> saved live data -> sample fallback data
```

That makes it useful for real clients, demos, and offline review.

### Screenshots / visual proof

![mqlaunch demo](docs/mqlaunch-demo.png)

![macos-scripts architecture](docs/macos-scripts-architecture.png)

These visuals show the broader operating style behind the client tools: command
surfaces, system maps, and workflows designed for fast operational scanning.

---

## What I Build

### Endpoint Readiness

Tools that make client state visible before production access fails.

* IGEL OS 12 and eLux baseline checks
* Citrix access readiness
* browser-visible endpoint signals
* local helper-assisted diagnostics
* support-friendly reports

### Automation Surfaces

Command surfaces that turn scattered scripts into structured workflows.

* terminal-native menus
* repeatable release checks
* repo intelligence workflows
* local assistant tooling
* safe operator prompts

### Systems Thinking

Practical architecture that respects security, support, usability, and real
operational constraints at the same time.

## Featured Project: macos-scripts

A terminal-first macOS automation toolkit built around `mqlaunch`, a modular
command surface for daily operations, release checks, diagnostics, and local AI
workflows.

![mqlaunch demo](docs/mqlaunch-demo.png)

```text
one command -> structured workflows -> repeatable execution
```

Repo: <https://github.com/MCamner/macos-scripts>  
Site: <https://mcamner.github.io/macos-scripts/>

Architecture:

![macos-scripts architecture](docs/macos-scripts-architecture.png)

* one entrypoint
* modular scripts underneath
* discoverable terminal workflows
* automation without hiding execution

---

## Design-Prototype Archive

Early browser-based prototypes for endpoint visibility, readiness checks,
compliance surfaces, and enterprise validation workflows. Origin lab for
several patterns now in production across the MQ stack.

Repo: <https://github.com/MCamner/Design-Prototype>  
Site: <https://mcamner.github.io/Design-Prototype/>

---

## Tool Highlights

### MQ Mirror

MQ Mirror translates macOS GUI actions into terminal command equivalents so
operators can learn, document, and execute faster.

```bash
tools/mqmirror/mqmirror network
tools/mqmirror/mqmirror inspect
tools/mqmirror/mqmirror watch --interval 1 --compact --ignore-terminal
```

```text
GUI action -> CLI equivalent -> better operational understanding
```

Part of:
<https://github.com/MCamner/Design-Prototype/tree/main/tools/mqmirror>

### MQ Client Optimizer

MQ Client Optimizer evaluates IGEL OS 12 and macOS clients against structured
baselines covering Citrix readiness, certificate health, and CIS-style security
compliance.

```bash
python3 tools/mq-client-optimizer/mq_client_optimizer.py list-baselines
python3 tools/mq-client-optimizer/mq_client_optimizer.py analyze \
  --baseline macos-enterprise-cis-lite \
  --sample
python3 tools/mq-client-optimizer/mq_client_optimizer.py serve
```

```text
client data -> baseline evaluation -> scored report
```

Part of:
<https://github.com/MCamner/Design-Prototype/tree/main/tools/mq-client-optimizer>

---

## Case Thinking

* `macos-scripts`
  Problem: useful scripts were scattered.
  Approach: one modular command surface.
  Result: faster discovery and repeatable execution.
* `Client readiness`
  Problem: enterprise clients fail when readiness is assumed.
  Approach: browser plus helper validation.
  Result: clear support signals before access breaks.
* `Endpoint validation`
  Problem: client posture is hard to explain under pressure.
  Approach: baselines, profiles, and reports.
  Result: shared language for operators and architects.
* `GUI-to-CLI learning`
  Problem: GUI actions hide operational commands.
  Approach: mirror actions as terminal equivalents.
  Result: better documentation and operator confidence.
* `Stack health`
  Problem: repo quality drifts invisibly across the stack.
  Approach: automated sweep, history, alerts, and CI gates.
  Result: regression caught before it reaches release.

---

## Technical Shape

* **Endpoint & EUC:** Citrix, IGEL OS, eLux, Intune, SCCM
* **Infrastructure:** Active Directory, VMware, Windows, Linux
* **Security:** Zero Trust, certificates, identity, access patterns
* **Automation:** Python, Bash, Zsh, CLI workflows
* **Architecture:** client readiness, validation, structured systems

---

## Repo Structure

```text
docs/       GitHub Pages site and browser readiness tools
helper/     read-only local helper agents and baseline logic
tests/      Python tests for helper behavior
cases/      short case notes and architecture narratives
bin/        local command entrypoints
```

The site is served via GitHub Pages from:

```text
main /docs
```

Release flow:

```bash
./release.sh --dry-run <version>
./release.sh <version>
```

## Roadmap

Near-term: keep tightening client readiness diagnostics, improve the static Pages
experience, and turn the strongest endpoint validation patterns into reusable case
studies under [`cases/`](cases/).

For the MQ stack: the stack control plane is now CI-enforced on
`mq-agent` main —
`sweep`, `history`, `alert`, `report`, `release-check`, `release-notes`, and
`contract-check` are covered by one orchestrator, with GitHub Actions running
`contract-check` and `release-check` on PRs and pushes to `main`.

Next MQ focus: formalize the v1.12 release notes and add an mqobsidian stack truth
export so CI/local gate results become long-term architecture memory.

---

## How I Work

* reduce complexity instead of adding layers
* make operational state visible
* balance security with usability
* build tools that can be explained under pressure
* prefer repeatable workflows over heroic manual fixes

```text
real problems -> real constraints -> practical systems
```

---

## Connect

* Website: <https://mcamner.com>
* LinkedIn: <https://www.linkedin.com/in/mattias-camner-75958022>
* Art platform: <https://blackiris.se>

---

## Motto

> Build things that work. Then make them impossible to break.

---

## Security

This repo is a static GitHub Pages project with local helper scripts for client
readiness workflows. Do not commit personal notes, customer data, credentials,
private endpoint details, or collected live diagnostics unless they are sanitized
and intended for publication.

---

## License

MIT

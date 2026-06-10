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

---

## In short

I build local-first tools for endpoint readiness, automation, and AI-assisted operations.

My work focuses on turning messy infrastructure signals into clear, repeatable actions
for support, architecture, and operations teams.

The MQ stack is the core of that work: eight repos that together take a local git repo
or operational screenshot and produce scored health signals, release gates, regression
alerts, and structured reviews — all without leaving the terminal.

---

## MQ Ecosystem Map

The MQ projects are a local-first toolchain for turning operational complexity
into visible state, safer decisions, and repeatable action.

```text
mqlaunch (macos-scripts)
    └──▶ mq-agent
              ├──▶ stack sweep ──▶ repo-signal (score each repo)
              │         └──▶ ~/.mq-agent/sweep-history.jsonl
              ├──▶ stack history / alert / report / release-check / release-notes
              └──▶ deep review ──▶ mq-mcp (tool runtime)
                                        ├──▶ repo-signal
                                        ├──▶ mq-image-analyze
                                        └──▶ mq-hal / mq-ums
```

| Repo | Role | Version | Status |
| --- | --- | --- | --- |
| [macos-scripts](https://github.com/MCamner/macos-scripts) | Terminal entrypoint — `mqlaunch` menus, stack cockpit, workflow chains | v1.0.0 | B2 Stack Cockpit; menu item 18 runs the full stack sweep pipeline |
| [mq-agent](https://github.com/MCamner/mq-agent) | Orchestrator — stack sweeps, health history, regression alerts, release gates, release notes, code review | v1.10.0 | Stack health pipeline complete: `sweep → history → alert → report → release-check → release-notes` |
| [mq-mcp](https://github.com/MCamner/mq-mcp) | Deterministic tool runtime — safety classes, contracts, 95+ documented tools | v1.11.0 | Learning contract layer; strong contract governance across the stack |
| [repo-signal](https://github.com/MCamner/repo-signal) | Repo intelligence — README quality, publish readiness, AI context exports | v1.4.0 | Stable scoring engine; powers `mq-agent stack sweep` per-repo scores |
| [mq-image-analyze](https://github.com/MCamner/mq-image-analyze) | Visual perception — OCR, diagrams, screenshots, architecture review | v1.4.0 | `image_ocr` MCP tool integrated into mq-agent review flow |
| [mq-hal](https://github.com/MCamner/mq-hal) | Operator layer — safe natural-language command routing | v1.2.0 | Vector-store health and stack status checks |
| [mq-ums](https://github.com/MCamner/mq-ums) | Browser UI for IGEL UMS operations via allowlisted PowerShell | v0.1.4 | Operator surface validated against live UMS |
| [atlas-one](https://github.com/MCamner/atlas-one) | Prompt routing studio — structured reasoning and reusable AI workflows | v1.4.0 | MQ ecosystem integration; personal workflow packs |

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
            └──▶ repo-signal scores each repo     (local, no key)
            └──▶ history written to JSONL          (~/.mq-agent/sweep-history.jsonl)
  └──▶ mq-agent stack alert                        (compare last two sweeps)
  └──▶ mq-agent stack report                       (score + trend + alert + ready per repo)
  └──▶ mq-agent stack release-check                (VERSION, CHANGELOG, branch, clean tree)
  └──▶ mq-agent stack release-notes                 (commits since last tag, per repo)
```

History persists across runs — trend and regression data accumulates automatically.

---

## What This Repo Is

This repository powers the `mcamner.github.io/MCamner` GitHub Pages site and a
set of browser-based client readiness tools under `docs/`.

It is both:

- a technical profile for my systems and automation work
- a working static toolkit for endpoint readiness and validation demos

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

- [`docs/index.html`](docs/index.html) - landing page for the client tools
- [`docs/client-readiness-check.html`](docs/client-readiness-check.html) - v1 browser readiness check
- [`docs/client-readiness-v2.html`](docs/client-readiness-v2.html) - multi-profile diagnostics

Helper entrypoints:

- [`helper/client_readiness_agent.py`](helper/client_readiness_agent.py) - local read-only helper API
- [`helper/client_readiness_agent_v2.py`](helper/client_readiness_agent_v2.py) - v2 data collector
- [`helper/client_helper.py`](helper/client_helper.py) - experimental helper surface

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

- IGEL OS 12 and eLux baseline checks
- Citrix access readiness
- browser-visible endpoint signals
- local helper-assisted diagnostics
- support-friendly reports

### Automation Surfaces

Command surfaces that turn scattered scripts into structured workflows.

- terminal-native menus
- repeatable release checks
- repo intelligence workflows
- local assistant tooling
- safe operator prompts

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

- one entrypoint
- modular scripts underneath
- discoverable terminal workflows
- automation without hiding execution

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

| Area | Problem | Approach | Result |
| --- | --- | --- | --- |
| macos-scripts | Scripts were useful but scattered | One modular command surface | Faster discovery and repeatable execution |
| Client readiness | Enterprise clients fail when readiness is assumed | Browser + helper validation | Clear support signals before access breaks |
| Endpoint validation | Client posture is hard to explain under pressure | Baselines, profiles, reports | Shared language for operators and architects |
| GUI-to-CLI learning | GUI actions hide operational commands | Mirror actions as terminal equivalents | Better documentation and operator confidence |
| Stack health | Repo quality drifts invisibly across eight repos | Automated sweep + history + alerts | Regression caught before it reaches release |

---

## Technical Shape

- **Endpoint & EUC:** Citrix, IGEL OS, eLux, Intune, SCCM
- **Infrastructure:** Active Directory, VMware, Windows, Linux
- **Security:** Zero Trust, certificates, identity, access patterns
- **Automation:** Python, Bash, Zsh, CLI workflows
- **Architecture:** client readiness, validation, structured systems

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

For the MQ stack: the release pipeline is stable at v1.10.0 — sweep, history, alert, report, release-check, and release-notes all ship from one orchestrator. Next focus is tightening the contracts between repos and exploring CI integration of `stack alert`.

---

## How I Work

- reduce complexity instead of adding layers
- make operational state visible
- balance security with usability
- build tools that can be explained under pressure
- prefer repeatable workflows over heroic manual fixes

```text
real problems -> real constraints -> practical systems
```

---

## Connect

- Website: <https://mcamner.com>
- LinkedIn: <https://www.linkedin.com/in/mattias-camner-75958022>
- Art platform: <https://blackiris.se>

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


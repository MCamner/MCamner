# Mattias Camner

Infrastructure architect building practical systems for endpoint readiness,
Zero Trust operations, client validation, and terminal-native automation.

```text
complex enterprise environment -> clear signals -> repeatable action
```

[![Pages](https://img.shields.io/badge/pages-live-174c5a)](https://mcamner.github.io/MCamner/)
[![Focus](https://img.shields.io/badge/focus-EUC%20%7C%20Zero%20Trust%20%7C%20Automation-orange)](#what-i-build)
[![Status](https://img.shields.io/badge/status-active-success)](#quick-start)

I work where infrastructure, security, endpoint platforms, and operations meet:
Citrix, IGEL OS, eLux, Intune, identity, certificates, client health, and the
messy last mile where systems either work for users or quietly fail.

---

## In short

I build local-first tools for endpoint readiness, automation, and AI-assisted operations.

My work focuses on turning messy infrastructure signals into clear, repeatable actions
for support, architecture, and operations teams.

---

## MQ Ecosystem Map

The MQ projects are a local-first toolchain for turning operational complexity
into visible state, safer decisions, and repeatable action.

```text
mqlaunch -> mq-agent -> mq-mcp
              |          |
              v          v
          repo-signal  mq-image-analyze
              |
              v
            mq-hal
```

| Repo | Role | Current status | Next focus |
| --- | --- | --- | --- |
| [macos-scripts](https://github.com/MCamner/macos-scripts) | Human terminal entrypoint through `mqlaunch` menus, checks, and workflows | v0.4.12; release-check and README readiness are green | v0.5.0 review-routing release and stronger release gates |
| [mq-agent](https://github.com/MCamner/mq-agent) | Orchestration layer for planning, execution, verification, safety, and memory | v1.3.0; architecture memory and model-selection workflows | v1.4.0 perception integration with `mq-image-analyze` |
| [mq-mcp](https://github.com/MCamner/mq-mcp) | Deterministic tool/runtime layer with safety classes, contracts, review, and memory | v1.10.0; learning contract layer and 95 documented tools | Release Gate v2 and stronger contract governance |
| [mq-hal](https://github.com/MCamner/mq-hal) | Local operator/status layer for safe natural-language command routing | v1.2.0; vector-store health and stack status | Roadmap cleanup and clearer stack-health reports |
| [mq-ums](https://github.com/MCamner/mq-ums) | Browser UI for IGEL UMS operations through allowlisted PowerShell commands | v0.1.4 RC; live UMS validation | v0.2.0 daily-use operator UI |
| [mq-image-analyze](https://github.com/MCamner/mq-image-analyze) | Visual perception layer for screenshots, OCR, diagrams, and architecture review | v1.3.0; `image_ocr` MCP tool and mq-agent examples | Broader perception workflows inside mq-agent/mq-mcp |
| [repo-signal](https://github.com/MCamner/repo-signal) | Repo intelligence engine for README quality, publish readiness, and AI context exports | v1.1.0; symbolic intelligence exports | Keep repo-quality contracts stable across the MQ stack |
| [atlas-one](https://github.com/MCamner/atlas-one) | Prompt routing studio for structured reasoning and reusable AI workflows | v0.6.0; MQ ecosystem integration | v0.7.0 personal workflow packs |

Together, these repos describe one operating pattern:

```text
local repo / endpoint / screenshot -> structured signal -> reviewed action
```

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

Near-term direction: keep tightening client readiness diagnostics, improve the
static Pages experience, and turn the strongest endpoint validation patterns
into reusable case studies under [`cases/`](cases/).

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

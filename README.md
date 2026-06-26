# Mattias Camner

<div align="center">

### Infrastructure / Endpoint / Automation Architect  
**Local-first automation · Endpoint readiness · Repo intelligence · Governed AI operations**

I build practical systems for the operational last mile — where infrastructure, endpoints, certificates, identity, automation, and real users either connect or fail.

<pre>
        enterprise complexity
                  │
                  ▼
   ╭──────────────────────────╮
   │   operational signal      │
   │   scored readiness        │
   │   safe automation         │
   │   reviewed action         │
   ╰──────────────────────────╯
                  │
                  ▼
      long-term technical memory
</pre>

[Journal](https://mcamner.github.io/mcamner-journal/) ·
[LinkedIn](https://www.linkedin.com/in/mattias-camner-75958022) ·
[Black Iris](https://blackiris.se/)

</div>

---

## What I build

I build local-first systems for infrastructure validation, endpoint readiness, repo intelligence, and AI-assisted operations.

The common thread is simple:

<pre>
repo / endpoint / screenshot / workflow
→ structured signal
→ scored readiness
→ reviewable action
→ long-term operational memory
</pre>

I care about tools that make state visible, decisions explainable, and automation safe enough to trust under real operational pressure.

---

## Main focus areas

- Endpoint readiness and client validation
- Citrix, IGEL OS, eLux, Intune, certificates, and identity-aware troubleshooting
- Local-first automation with Bash, PowerShell, Python, and terminal workflows
- Repo health, release gates, contract checks, and readiness scoring
- MCP tooling, policy gates, safety classes, and controlled AI tool execution
- Obsidian-based technical memory and long-term architecture knowledge
- Practical systems that operators can understand, repeat, and improve

---

## The MQ ecosystem

The **MQ stack** is my local-first operating layer for infrastructure work, repo intelligence, and governed AI-assisted engineering.

It turns local technical work into structured signals, release checks, review outputs, and reusable knowledge.

| Repository | Purpose |
|---|---|
| [`macos-scripts`](https://github.com/MCamner/macos-scripts) | Terminal entrypoint, launcher menus, local workflows, and system tools |
| [`mq-agent`](https://github.com/MCamner/mq-agent) | Terminal-native orchestrator for sweeps, release gates, alerts, reviews, and workflow execution |
| [`mq-mcp`](https://github.com/MCamner/mq-mcp) | Deterministic MCP runtime for safe tool execution, policy gates, contracts, and local AI governance |
| [`repo-signal`](https://github.com/MCamner/repo-signal) | Repo readiness scoring, release checks, and AI-context exports |
| [`mq-image-analyze`](https://github.com/MCamner/mq-image-analyze) | Screenshot, OCR, UI, and visual-analysis tooling for agents and operators |
| [`mq-ums`](https://github.com/MCamner/mq-ums) | Local operator UI for IGEL UMS workflows using allowlisted PowerShell actions |
| [`mq-hal`](https://github.com/MCamner/mq-hal) | Natural-language operator layer for safe local command routing |
| [`atlas-one`](https://github.com/MCamner/atlas-one) | Prompt routing studio and structured AI workflow design |
| [`mqobsidian`](https://github.com/MCamner/mqobsidian) | Obsidian-based single source of truth for stack memory, decisions, and system context |

<div align="center">

![macos-scripts architecture](docs/macos-scripts-architecture.png)

<sub>One entrypoint, layered workflows — the operating model the MQ stack is built on.</sub>

</div>

---

## Core architecture idea

Modern infrastructure rarely fails because of one obvious thing.

It usually fails because something is almost right:

- the endpoint is almost ready
- the certificate chain is almost trusted
- the client is almost compliant
- the release is almost safe
- the documentation is almost current
- the AI-generated answer is almost correct
- the repo is almost ready to ship

My work is about closing those gaps.

<pre>
almost ready
→ measured
→ explained
→ corrected
→ repeatable
</pre>

---

## Operating principles

### 1. Signal before action

Do not automate blindly.  
Collect the signal, score the state, explain the risk, then make the next action clear.

### 2. Local-first by default

Useful tools should work from the operator’s machine, against real files, real repos, and real endpoint signals.

### 3. Human-reviewed automation

AI can assist, summarize, compare, and propose.  
Critical action should remain gated, inspectable, and reversible.

### 4. Boring safety is good safety

Tool execution should be explicit, policy-bound, logged, and predictable.

### 5. Memory beats repetition

Good engineering is not only code.  
It is also decisions, failures, fixes, release notes, lessons learned, and patterns that survive the next work session.

---

## Selected project story

### macos-scripts

A modular terminal launcher for structured local workflows on macOS.

It acts as the practical front door into the MQ ecosystem: menus, repo workflows, local scripts, diagnostics, and stack control.

Repo: [`macos-scripts`](https://github.com/MCamner/macos-scripts)

---

### mq-agent

A terminal-native orchestrator for repo sweeps, release gates, workflow execution, alerts, reviews, and stack reporting.

It coordinates local tools without hiding what is happening.

Repo: [`mq-agent`](https://github.com/MCamner/mq-agent)

---

### mq-mcp

A deterministic MCP runtime focused on safe tool execution, policy gates, contracts, and controlled local AI workflows.

The goal is not magic.  
The goal is predictable tool use with clear boundaries.

Repo: [`mq-mcp`](https://github.com/MCamner/mq-mcp)

---

### repo-signal

A repo intelligence engine for readiness scoring, release checks, and AI-context exports.

It turns repository state into structured information that can be used by humans, agents, CI gates, and documentation workflows.

Repo: [`repo-signal`](https://github.com/MCamner/repo-signal)

---

### mq-image-analyze

A visual reasoning toolkit for screenshots, OCR, UI states, diagrams, and operational image analysis.

Useful when the signal is not only in code or text, but in what the user or operator sees.

Repo: [`mq-image-analyze`](https://github.com/MCamner/mq-image-analyze)

---

### mq-ums

A local operator interface for IGEL UMS workflows using allowlisted PowerShell actions, review gates, and endpoint-management automation.

The goal is safer endpoint operations through controlled action surfaces.

Repo: [`mq-ums`](https://github.com/MCamner/mq-ums)

---

## Example workflow

<pre>
terminal
→ mqlaunch
→ mq-agent stack sweep
→ repo-signal scores each repo
→ mq-agent reports trend, readiness, alerts, and blockers
→ release gates catch drift before merge
→ mqobsidian stores long-term architecture memory
</pre>

The pattern:

<pre>
local work
→ structured signal
→ review
→ gate
→ memory
→ better future context
</pre>

---

## Technical shape

### Endpoint and EUC

- Citrix Workspace
- IGEL OS / UMS
- eLux
- Intune
- Client readiness
- Certificates
- Identity and access patterns
- Windows, macOS, and Linux operations

### Automation

- Python
- Bash / Zsh
- PowerShell
- Local CLIs
- GitHub Actions
- Static sites and browser tools
- Release and contract validation

### AI-assisted engineering

- MCP runtimes
- Prompt routing
- Local context packs
- Policy gates
- Safety classes
- Human-in-the-loop workflows
- Obsidian-based technical memory

---

## How I think about systems

I prefer systems that are:

- clear over clever
- inspectable over magical
- repeatable over heroic
- safe by default
- useful in real operations
- easy to explain under pressure

The best tools make good behavior easier than risky behavior.

---

## Current direction

The next stage of my work is about connecting local repositories, endpoint operations, AI-assisted review, and Obsidian memory into one coherent operating model.

The target is a practical architecture loop:

<pre>
work session
→ repo or endpoint signal
→ review output
→ gate result
→ decision record
→ reusable memory
→ better next action
</pre>

This is the direction behind the MQ stack.

---

## Connect

- GitHub Pages / journal: [mcamner.github.io/mcamner-journal](https://mcamner.github.io/mcamner-journal/)
- LinkedIn: [Mattias Camner](https://www.linkedin.com/in/mattias-camner-75958022)
- Art platform: [blackiris.se](https://blackiris.se/)

---

## Security note

These repositories are public portfolio and tooling projects.

Do not commit customer data, credentials, private endpoint details, internal hostnames, production diagnostics, personal notes, or unsanitized operational exports.

---

## Motto

Build things that work.  
Then make the correct action easy to repeat.

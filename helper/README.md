# Client Readiness Agent

Small read-only Python helper for the browser-based client readiness page.

## Purpose

The HTML page can only see browser-visible signals. This helper exposes a local JSON endpoint on `localhost` so the page can enrich its checks with host-level information such as:

* hostname
* platform details
* local OS release data
* simple client-family heuristics
* local IP addresses
* categorized checks for network, browser, certificates, Citrix, and management
* optional baseline comparison through `client_readiness_baseline.json`
* named baseline profiles from `helper/baselines/`

## Run

```bash
python3 helper/client_readiness_agent.py
```

Select a named baseline:

```bash
python3 helper/client_readiness_agent.py --baseline igel-os12
python3 helper/client_readiness_agent.py --baseline elux7
```

Default endpoint:

```text
http://127.0.0.1:38765/status
```

Health endpoint:

```text
http://127.0.0.1:38765/health
```

## Notes

* The agent is read-only.
* It uses Python standard library only.
* The browser page will fall back to browser-only checks if the helper is not running.
* The current version uses practical heuristics and known local paths for IGEL/eLux-style environments.
* Baseline-driven checks can mark required items as `fail` when they drift from the expected client profile.

## Recommended Placement

For centrally managed thin clients, the agent should live in the customer/persistent area rather than in random system paths.

### IGEL OS 12

Suggested location:

```text
/custom/client-readiness/
```

Suggested command:

```bash
/usr/bin/python3 /custom/client-readiness/client_readiness_agent.py --baseline igel-os12
```

Example launcher script:
[helper/deploy/igel-os12-launch.sh](../helper/deploy/igel-os12-launch.sh)

### eLux 7

Suggested location:

```text
/setup/client-readiness/
```

Suggested command:

```bash
/usr/bin/python3 /setup/client-readiness/client_readiness_agent.py --baseline elux7
```

Example launcher script:
[helper/deploy/elux7-launch.sh](../helper/deploy/elux7-launch.sh)

## Deployment Model

Recommended approach:

* deploy the helper centrally through UMS or Scout
* place it in the platform-appropriate persistent area
* start it with the matching named baseline
* let the browser page connect to `localhost`

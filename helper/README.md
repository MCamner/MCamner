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

### Local status server

```bash
python3 helper/client_readiness_agent.py
```

Select a named baseline:

```bash
python3 helper/client_readiness_agent.py --baseline igel-os12
python3 helper/client_readiness_agent.py --baseline elux7
```

Named baselines are the preferred path for real client profiles.
`client_readiness_baseline.json` is best treated as a generic fallback or local custom override.

Default endpoint:

```text
http://127.0.0.1:38765/status
```

Health endpoint:

```text
http://127.0.0.1:38765/health
```

### Serve v2 diagnostics

The v2 page requires `client-readiness.v2`; the legacy `client_readiness_agent.py`
server returns a different contract and is rejected by that page. Stop the v1
server before starting v2 on the same port:

```bash
python3 helper/client_readiness_agent_v2.py --serve --profile igel-os12-citrix
```

The v2 server binds to `127.0.0.1:38765`, with `/health` and `/status`.
It permits the public Pages origin and local previews on port 8000. Add
`--allow-origin http://localhost:PORT` for a different preview port.
The legacy v1 launch scripts remain for the v1 browser page.

Collection results distinguish `ERROR` (evidence collection failed),
`UNSUPPORTED` (collector unavailable), and `NOT_CHECKED` (missing evidence)
from an observed `FAIL`. Capabilities depend on the platform and installed
commands. Certificate expiry is not inferred from keychain modification dates;
without a real X.509 expiry value, that rule remains `NOT_CHECKED`.

### Generate v2 client data

`client_readiness_agent_v2.py` collects a v2 JSON payload for the multi-profile page in `docs/client-readiness-v2.html`.

Print JSON to the terminal:

```bash
python3 helper/client_readiness_agent_v2.py --profile igel-os12-citrix --pretty
```

Write the payload where the v2 page can load it as saved live data:

```bash
python3 helper/client_readiness_agent_v2.py --profile igel-os12-citrix --pretty --out docs/live-client-data.json
```

Available browser profiles are listed in:

```text
docs/profiles/index.json
```

## Notes

* The agent is read-only.
* It uses Python standard library only.
* The browser page will fall back to browser-only checks if the helper is not running.
* The v2 page validates the schema before accepting a source and loads data in this order: local helper endpoint, `docs/live-client-data.json`, then `docs/sample-client-data.json`.
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

## End-to-End Flow

1. Deploy the helper to the client.
2. Start it with the correct named baseline.
3. Open the readiness page from the client browser.
4. Confirm that the page shows helper connection and the expected baseline.
5. Review category status first, then drill into individual checks and recommended actions.

## Reports and repeatable checks

The v2 page marks live, saved, imported, and demo sources explicitly. Measurements
older than 15 minutes, future timestamps, and unknown collection times are
flagged. Existing saved fixtures have unknown collection times; no fresh time
has been invented for them.

Export JSON to preserve the complete measurement, profile snapshot, evaluation
time, and results. Import recalculates results from those inputs using the
original evaluation time, including time-sensitive certificate checks. Imports
are local and limited to 2 MB. HTML exports are standalone readable reports;
JSON is the re-importable format. Copy support summary has a manual fallback
when clipboard access is unavailable.

Known hostname, IP, path, certificate identity, and smartcard identity fields
are masked by default in exports. Masking is not a guarantee of anonymity:
review free text and report contents before sharing. Uncheck masking only when
an authorized recipient needs the full evidence. Masking can remove evidence
used by a custom rule; exported results are recalculated accordingly.

Run the checks without any customer data or live collection:

```bash
python3 -m pytest -q
node --test tests/test_readiness_v2.js
```

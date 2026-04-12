# Client Readiness Agent

Small read-only Python helper for the browser-based client readiness page.

## Purpose

The HTML page can only see browser-visible signals. This helper exposes a local JSON endpoint on `localhost` so the page can enrich its checks with host-level information such as:

* hostname
* platform details
* local OS release data
* simple client-family heuristics
* local IP addresses

## Run

```bash
python3 helper/client_readiness_agent.py
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

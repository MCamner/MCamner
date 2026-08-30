# Screenshots

This folder holds public visual proof of the MCamner client tools and
portfolio surfaces.

- [`client-readiness-v2.png`](client-readiness-v2.png) — the [Client
  Readiness Diagnostics v2](../client-readiness-v2.html) tool evaluating the
  built-in `igel-os12-citrix` profile, referenced from the main
  [README](../../README.md). It runs against `sample-client-data.json`
  (fully synthetic — no real device, hostname, or IP involved) so it always
  shows a clean 5/5 pass. Regenerate it by serving `docs/` locally and
  screenshotting the page, e.g. with Playwright:

  ```bash
  python3 -m http.server 8000 --directory docs &
  python3 - <<'PY'
  from playwright.sync_api import sync_playwright
  with sync_playwright() as p:
      page = p.chromium.launch().new_page(viewport={"width": 1200, "height": 1000}, device_scale_factor=2)
      page.goto("http://127.0.0.1:8000/client-readiness-v2.html", wait_until="networkidle")
      page.wait_for_timeout(1500)
      page.screenshot(path="docs/screenshots/client-readiness-v2.png", full_page=True)
  PY
  ```

  (this only reaches the sample-data tier if no `live-client-data.json` is
  present next to it — rename or remove that file first if you want the
  guaranteed-synthetic result rather than whatever is currently saved there)

Other visual assets used by the README live one level up:

- [`../mqlaunch-demo.png`](../mqlaunch-demo.png)
- [`../macos-scripts-architecture.png`](../macos-scripts-architecture.png)
- [`../operating-model.png`](../operating-model.png)

When adding client-readiness screenshots, keep them sanitized and avoid customer
names, internal hostnames, private IPs, serial numbers, usernames, or collected
live diagnostics. `../live-client-data.json` is real (but sanitized) tool
output kept for the "saved-live" fallback tier — its `hostname` and
`local_ips` fields were redacted to `client-01.local` / `192.0.2.10`; treat
any future update to that file as sensitive and sanitize it the same way
before committing.

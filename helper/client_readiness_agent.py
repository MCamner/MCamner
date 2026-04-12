#!/usr/bin/env python3

import argparse
import json
import os
import platform
import socket
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


HELPER_DIR = os.path.dirname(__file__)
DEFAULT_BASELINE_PATH = os.path.join(HELPER_DIR, "client_readiness_baseline.json")
BASELINES_DIR = os.path.join(HELPER_DIR, "baselines")
CURRENT_BASELINE_PATH = DEFAULT_BASELINE_PATH


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def status_priority(status):
    return {"fail": 0, "warn": 1, "ok": 2}.get(status, 1)


def collapse_status(statuses):
    result = "ok"
    for status in statuses:
        if status_priority(status) < status_priority(result):
            result = status
    return result


def read_json_file(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return {"available": True, "path": path, "values": json.load(handle)}
    except (OSError, json.JSONDecodeError):
        return {"available": False, "path": path, "values": {}}


def list_available_baselines():
    results = {}
    if not os.path.isdir(BASELINES_DIR):
        return results
    for filename in sorted(os.listdir(BASELINES_DIR)):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(BASELINES_DIR, filename)
        key = filename[:-5]
        payload = read_json_file(path)
        results[key] = {
            "available": payload["available"],
            "path": path,
            "name": payload["values"].get("name", key) if payload["available"] else key
        }
    return results


def resolve_baseline_path(name):
    if not name:
        return DEFAULT_BASELINE_PATH
    safe = os.path.basename(name)
    candidate = os.path.join(BASELINES_DIR, safe + ".json")
    if os.path.exists(candidate):
        return candidate
    return DEFAULT_BASELINE_PATH


def read_os_release():
    path = "/etc/os-release"
    data = {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or "=" not in line or line.startswith("#"):
                    continue
                key, value = line.split("=", 1)
                data[key] = value.strip().strip('"')
    except OSError:
        return {"available": False, "path": path, "values": {}}

    return {"available": True, "path": path, "values": data}


def detect_client_family(os_release):
    release_blob = " ".join(os_release.get("values", {}).values()).lower()
    heuristics = [
        ("IGEL (possible)", any(os.path.exists(path) for path in ("/etc/igel", "/opt/IGEL", "/opt/igel"))),
        ("eLux (possible)", any(os.path.exists(path) for path in ("/etc/elux", "/etc/unicon", "/opt/unicon"))),
    ]

    for label, matched in heuristics:
        if matched:
            return {"family": label, "confidence": "high"}

    if "igel" in release_blob:
        return {"family": "IGEL (possible)", "confidence": "medium"}
    if "elux" in release_blob or "unicon" in release_blob:
        return {"family": "eLux (possible)", "confidence": "medium"}
    if "linux" in release_blob:
        return {"family": "Linux client (generic)", "confidence": "low"}

    return {"family": "Unknown client family", "confidence": "low"}


def get_ip_addresses():
    addresses = []
    hostname = socket.gethostname()
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return addresses

    seen = set()
    for info in infos:
        address = info[4][0]
        if ":" in address or address.startswith("127."):
            continue
        if address not in seen:
            seen.add(address)
            addresses.append(address)
    return addresses


def file_exists(path):
    return os.path.exists(path)


def path_summary(paths):
    present = [path for path in paths if file_exists(path)]
    return {
        "present": present,
        "missing": [path for path in paths if path not in present]
    }


def read_file_lines(path, limit=20):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return [line.rstrip("\n") for _, line in zip(range(limit), handle)]
    except OSError:
        return []


def parse_proc_route():
    path = "/proc/net/route"
    if not os.path.exists(path):
        return {"available": False, "has_default_route": False}
    lines = read_file_lines(path, limit=10)
    has_default = any("\t00000000\t" in line for line in lines[1:])
    return {"available": True, "has_default_route": has_default}


def parse_resolv_conf():
    path = "/etc/resolv.conf"
    if not os.path.exists(path):
        return {"available": False, "nameservers": []}
    nameservers = []
    for line in read_file_lines(path, limit=20):
        parts = line.split()
        if len(parts) >= 2 and parts[0] == "nameserver":
            nameservers.append(parts[1])
    return {"available": True, "nameservers": nameservers}


def find_proxy_hints():
    hints = []
    for key in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        value = os.environ.get(key)
        if value:
            hints.append(f"{key}={value}")
    return hints


def make_check(category, name, status, summary, details, baseline_required=False, recommended_action=""):
    return {
        "category": category,
        "name": name,
        "status": status,
        "summary": summary,
        "details": details,
        "baseline_required": baseline_required,
        "recommended_action": recommended_action
    }


def base_checks(os_release, addresses, detection):
    return [
        make_check(
            "agent",
            "Agent process",
            "ok",
            "Local helper agent is running",
            ["Read-only Python helper is serving JSON on localhost."],
            recommended_action="Keep the agent running locally on the client."
        ),
        make_check(
            "agent",
            "Hostname",
            "ok" if socket.gethostname() else "warn",
            socket.gethostname() or "Hostname unavailable",
            ["Collected from Python socket hostname lookup."],
            recommended_action="Ensure hostname is available for support identification."
        ),
        make_check(
            "os",
            "OS release",
            "ok" if os_release["available"] else "warn",
            os_release["path"] if os_release["available"] else "Could not read /etc/os-release",
            [
                "PRETTY_NAME: " + os_release["values"].get("PRETTY_NAME", "Unavailable"),
                "ID: " + os_release["values"].get("ID", "Unavailable")
            ],
            recommended_action="Verify OS identification path or use platform-specific paths if /etc/os-release is unavailable."
        ),
        make_check(
            "network",
            "IP addresses",
            "ok" if addresses else "warn",
            ", ".join(addresses) if addresses else "No non-loopback IPv4 addresses found",
            ["Collected from local hostname address resolution."],
            recommended_action="Check network attachment, hostname resolution, and interface state."
        ),
        make_check(
            "os",
            "Client family",
            "ok" if detection["confidence"] == "high" else "warn",
            detection["family"] + " (" + detection["confidence"] + " confidence)",
            ["Based on local paths and /etc/os-release heuristics."],
            recommended_action="Add clearer platform-specific paths or baseline expectations if confidence remains low."
        )
    ]


def network_checks():
    route_info = parse_proc_route()
    resolv_info = parse_resolv_conf()
    proxy_hints = find_proxy_hints()

    return [
        make_check(
            "network",
            "Default route",
            "ok" if route_info["has_default_route"] else "warn",
            "Default route present" if route_info["has_default_route"] else "No default route detected",
            ["/proc/net/route checked" if route_info["available"] else "/proc/net/route not available on this platform"],
            recommended_action="Check routing or platform-specific route inspection."
        ),
        make_check(
            "network",
            "DNS resolvers",
            "ok" if resolv_info["nameservers"] else "warn",
            ", ".join(resolv_info["nameservers"]) if resolv_info["nameservers"] else "No nameservers found",
            ["/etc/resolv.conf parsed" if resolv_info["available"] else "/etc/resolv.conf not available"],
            recommended_action="Ensure DNS resolvers are present and aligned with the expected client baseline."
        ),
        make_check(
            "network",
            "Proxy hints",
            "warn" if proxy_hints else "ok",
            "Proxy variables present" if proxy_hints else "No proxy variables detected",
            proxy_hints if proxy_hints else ["No http_proxy/https_proxy environment hints found."],
            recommended_action="Check whether a proxy is expected for browser, IdP, or Citrix access in this environment."
        )
    ]


def browser_checks():
    browser_paths = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/firefox"
    ]
    info = path_summary(browser_paths)
    return [
        make_check(
            "browser",
            "Known browser binaries",
            "ok" if info["present"] else "warn",
            ", ".join(info["present"]) if info["present"] else "No known browser paths found",
            ["Present: " + ", ".join(info["present"]) if info["present"] else "No matching browser paths detected."],
            recommended_action="Verify which browser is installed or adjust baseline paths for the client platform."
        )
    ]


def certificate_checks():
    certificate_targets = {
        "Browser certificates": ["/setup/cacerts/browser", "/setup/cacerts"],
        "Citrix certificates": ["/setup/cacerts/intcerts", "/setup/cacerts"],
        "Smartcard login certificates": ["/setup/cacerts/login"]
    }

    checks = []
    for name, targets in certificate_targets.items():
        info = path_summary(targets)
        checks.append(
            make_check(
                "certificates",
                name,
                "ok" if info["present"] else "warn",
                ", ".join(info["present"]) if info["present"] else "No expected path present",
                ["Missing: " + ", ".join(info["missing"]) if info["missing"] else "All expected paths are present."],
                recommended_action="Verify required CA, browser, Citrix, or smartcard certificate locations."
            )
        )
    return checks


def citrix_checks():
    targets = [
        "/setup/ica",
        "/setup/ica/AuthManConfig.xml"
    ]
    info = path_summary(targets)
    return [
        make_check(
            "citrix",
            "Citrix config paths",
            "ok" if info["present"] else "warn",
            ", ".join(info["present"]) if info["present"] else "No Citrix config paths detected",
            ["Missing: " + ", ".join(info["missing"]) if info["missing"] else "All expected Citrix paths are present."],
            recommended_action="Validate Citrix Workspace / ICA configuration paths on the client."
        )
    ]


def management_checks(detection):
    if "IGEL" in detection["family"]:
        targets = ["/etc/igel", "/opt/IGEL", "/opt/igel"]
        label = "IGEL local management paths"
    elif "eLux" in detection["family"]:
        targets = ["/etc/unicon", "/etc/elux", "/setup"]
        label = "eLux local management paths"
    else:
        targets = ["/etc/unicon", "/etc/elux", "/etc/igel", "/opt/IGEL", "/setup"]
        label = "Known management paths"

    info = path_summary(targets)
    return [
        make_check(
            "management",
            label,
            "ok" if info["present"] else "warn",
            ", ".join(info["present"]) if info["present"] else "No known management paths detected",
            ["Missing: " + ", ".join(info["missing"]) if info["missing"] else "Management-relevant paths found."],
            recommended_action="Verify UMS, Scout, or local management-relevant paths for the expected client family."
        )
    ]


def summarize_categories(checks):
    categories = {}
    for check in checks:
        category = check["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(check)

    result = {}
    for category, category_checks in categories.items():
        result[category] = {
            "status": collapse_status([check["status"] for check in category_checks]),
            "count": len(category_checks)
        }
    return result


def apply_baseline(checks, detection, baseline, dns_info, route_info, proxy_hints):
    expected_family = baseline.get("expectedClientFamily", "").strip().lower()
    if expected_family:
        for check in checks:
            if check["name"] == "Client family":
                actual = detection["family"].lower()
                if expected_family in actual:
                    check["details"].append("Baseline: client family matches expected value.")
                else:
                    check["status"] = "fail"
                    check["baseline_required"] = True
                    check["details"].append("Baseline mismatch: expected client family containing '" + baseline["expectedClientFamily"] + "'.")
                    check["recommended_action"] = "Confirm device family or assign the correct baseline."

    required_paths = baseline.get("requiredPathsByCategory", {})
    for category, paths in required_paths.items():
        for path in paths:
            matching = [check for check in checks if check["category"] == category and path in " ".join(check["details"] + [check["summary"]])]
            if matching:
                for check in matching:
                    check["baseline_required"] = True
            elif paths:
                checks.append(
                    make_check(
                        category,
                        "Baseline required path",
                        "fail",
                        "Required path missing: " + path,
                        ["Baseline requires this path, but no existing check reported it present."],
                        baseline_required=True,
                        recommended_action="Verify that the required path exists on the client or update the baseline."
                    )
                )

    required_dns = baseline.get("requiredDnsResolvers", [])
    if required_dns:
        present_dns = set(dns_info.get("nameservers", []))
        missing_dns = [value for value in required_dns if value not in present_dns]
        checks.append(
            make_check(
                "network",
                "Baseline DNS resolvers",
                "ok" if not missing_dns else "fail",
                "All required DNS resolvers present" if not missing_dns else "Missing required DNS resolvers",
                ["Missing: " + ", ".join(missing_dns) if missing_dns else "Required resolvers are present."],
                baseline_required=True,
                recommended_action="Align resolver configuration with the expected environment baseline."
            )
        )

    if baseline.get("requireDefaultRoute"):
        checks.append(
            make_check(
                "network",
                "Baseline default route",
                "ok" if route_info.get("has_default_route") else "fail",
                "Default route present" if route_info.get("has_default_route") else "Default route required by baseline but not detected",
                ["Baseline requires a default route."],
                baseline_required=True,
                recommended_action="Verify routing or use a platform-specific route check if this is a managed client."
            )
        )

    if baseline.get("requireProxyHints"):
        checks.append(
            make_check(
                "network",
                "Baseline proxy expectation",
                "ok" if proxy_hints else "fail",
                "Proxy hints detected" if proxy_hints else "Proxy hints required by baseline but not detected",
                proxy_hints if proxy_hints else ["No proxy environment variables found."],
                baseline_required=True,
                recommended_action="Verify proxy settings for browser, IdP, and Citrix access."
            )
        )

    return checks


def collect_status(selected_baseline=None):
    baseline_path = resolve_baseline_path(selected_baseline) if selected_baseline else CURRENT_BASELINE_PATH
    baseline_file = read_json_file(baseline_path)
    baseline = baseline_file["values"] if baseline_file["available"] else {}
    os_release = read_os_release()
    detection = detect_client_family(os_release)
    addresses = get_ip_addresses()
    dns_info = parse_resolv_conf()
    route_info = parse_proc_route()
    proxy_hints = find_proxy_hints()

    checks = []
    checks.extend(base_checks(os_release, addresses, detection))
    checks.extend(network_checks())
    checks.extend(browser_checks())
    checks.extend(certificate_checks())
    checks.extend(citrix_checks())
    checks.extend(management_checks(detection))
    checks = apply_baseline(checks, detection, baseline, dns_info, route_info, proxy_hints)

    categories = summarize_categories(checks)
    overall = collapse_status([entry["status"] for entry in categories.values()]) if categories else "warn"

    return {
        "timestamp": utc_now(),
        "agent": {
            "name": "client-readiness-agent",
            "version": "0.4.0",
            "mode": "read-only"
        },
        "hostname": socket.gethostname(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python": platform.python_version()
        },
        "baseline": {
          "available": baseline_file["available"],
          "path": baseline_file["path"],
          "name": baseline.get("name", os.path.basename(baseline_path)),
          "notes": baseline.get("notes", ""),
          "selected": selected_baseline or os.path.splitext(os.path.basename(baseline_path))[0]
        },
        "available_baselines": list_available_baselines(),
        "os_release": os_release,
        "client_detection": detection,
        "ip_addresses": addresses,
        "overall_status": overall,
        "categories": categories,
        "checks": checks
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "ClientReadinessAgent/0.4"

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        baseline = query.get("baseline", [""])[0].strip()

        if parsed.path == "/health":
            self._send_json({"status": "ok", "timestamp": utc_now()})
            return
        if parsed.path == "/status":
            self._send_json(collect_status(selected_baseline=baseline or None))
            return
        self._send_json({"error": "Not found", "path": self.path}, status=404)

    def log_message(self, format_string, *args):
        return


def main():
    global CURRENT_BASELINE_PATH

    parser = argparse.ArgumentParser(description="Local read-only helper for the client readiness page.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host, default: 127.0.0.1")
    parser.add_argument("--port", default=38765, type=int, help="Bind port, default: 38765")
    parser.add_argument("--baseline", default="", help="Baseline name from helper/baselines or explicit baseline file path")
    args = parser.parse_args()

    if args.baseline:
        if os.path.isfile(args.baseline):
            CURRENT_BASELINE_PATH = args.baseline
        else:
            CURRENT_BASELINE_PATH = resolve_baseline_path(args.baseline)

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Client readiness agent listening on http://{args.host}:{args.port}")
    print(f"Using baseline: {CURRENT_BASELINE_PATH}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

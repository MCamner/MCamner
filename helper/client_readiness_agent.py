#!/usr/bin/env python3

import argparse
import json
import os
import platform
import socket
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


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


def make_check(category, name, status, summary, details):
    return {
        "category": category,
        "name": name,
        "status": status,
        "summary": summary,
        "details": details
    }


def base_checks(os_release, addresses, detection):
    return [
        make_check(
            "agent",
            "Agent process",
            "ok",
            "Local helper agent is running",
            ["Read-only Python helper is serving JSON on localhost."]
        ),
        make_check(
            "agent",
            "Hostname",
            "ok" if socket.gethostname() else "warn",
            socket.gethostname() or "Hostname unavailable",
            ["Collected from Python socket hostname lookup."]
        ),
        make_check(
            "os",
            "OS release",
            "ok" if os_release["available"] else "warn",
            os_release["path"] if os_release["available"] else "Could not read /etc/os-release",
            [
                "PRETTY_NAME: " + os_release["values"].get("PRETTY_NAME", "Unavailable"),
                "ID: " + os_release["values"].get("ID", "Unavailable")
            ]
        ),
        make_check(
            "network",
            "IP addresses",
            "ok" if addresses else "warn",
            ", ".join(addresses) if addresses else "No non-loopback IPv4 addresses found",
            ["Collected from local hostname address resolution."]
        ),
        make_check(
            "os",
            "Client family",
            "ok" if detection["confidence"] == "high" else "warn",
            detection["family"] + " (" + detection["confidence"] + " confidence)",
            ["Based on local paths and /etc/os-release heuristics."]
        )
    ]


def network_checks():
    route_info = parse_proc_route()
    resolv_info = parse_resolv_conf()
    proxy_hints = find_proxy_hints()

    checks = [
        make_check(
            "network",
            "Default route",
            "ok" if route_info["has_default_route"] else "warn",
            "Default route present" if route_info["has_default_route"] else "No default route detected",
            ["/proc/net/route checked" if route_info["available"] else "/proc/net/route not available on this platform"]
        ),
        make_check(
            "network",
            "DNS resolvers",
            "ok" if resolv_info["nameservers"] else "warn",
            ", ".join(resolv_info["nameservers"]) if resolv_info["nameservers"] else "No nameservers found",
            ["/etc/resolv.conf parsed" if resolv_info["available"] else "/etc/resolv.conf not available"]
        ),
        make_check(
            "network",
            "Proxy hints",
            "warn" if proxy_hints else "ok",
            "Proxy variables present" if proxy_hints else "No proxy variables detected",
            proxy_hints if proxy_hints else ["No http_proxy/https_proxy environment hints found."]
        )
    ]
    return checks


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
            ["Present: " + ", ".join(info["present"]) if info["present"] else "No matching browser paths detected."]
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
                ["Missing: " + ", ".join(info["missing"]) if info["missing"] else "All expected paths are present."]
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
            ["Missing: " + ", ".join(info["missing"]) if info["missing"] else "All expected Citrix paths are present."]
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
            ["Missing: " + ", ".join(info["missing"]) if info["missing"] else "Management-relevant paths found."]
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


def collect_status():
    os_release = read_os_release()
    detection = detect_client_family(os_release)
    addresses = get_ip_addresses()

    checks = []
    checks.extend(base_checks(os_release, addresses, detection))
    checks.extend(network_checks())
    checks.extend(browser_checks())
    checks.extend(certificate_checks())
    checks.extend(citrix_checks())
    checks.extend(management_checks(detection))

    categories = summarize_categories(checks)
    overall = collapse_status([entry["status"] for entry in categories.values()]) if categories else "warn"

    return {
        "timestamp": utc_now(),
        "agent": {
            "name": "client-readiness-agent",
            "version": "0.2.0",
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
        "os_release": os_release,
        "client_detection": detection,
        "ip_addresses": addresses,
        "overall_status": overall,
        "categories": categories,
        "checks": checks
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "ClientReadinessAgent/0.2"

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
        if self.path == "/health":
            self._send_json({"status": "ok", "timestamp": utc_now()})
            return
        if self.path == "/status":
            self._send_json(collect_status())
            return
        self._send_json({"error": "Not found", "path": self.path}, status=404)

    def log_message(self, format_string, *args):
        return


def main():
    parser = argparse.ArgumentParser(description="Local read-only helper for the client readiness page.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host, default: 127.0.0.1")
    parser.add_argument("--port", default=38765, type=int, help="Bind port, default: 38765")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Client readiness agent listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

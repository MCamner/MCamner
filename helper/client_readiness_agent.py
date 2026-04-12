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


def local_checks(os_release, addresses, detection):
    checks = [
        {
            "name": "Agent process",
            "status": "ok",
            "summary": "Local helper agent is running",
            "details": ["Read-only Python helper is serving JSON on localhost."]
        },
        {
            "name": "Hostname",
            "status": "ok" if socket.gethostname() else "warn",
            "summary": socket.gethostname() or "Hostname unavailable",
            "details": ["Collected from Python socket hostname lookup."]
        },
        {
            "name": "OS release",
            "status": "ok" if os_release["available"] else "warn",
            "summary": os_release["path"] if os_release["available"] else "Could not read /etc/os-release",
            "details": [
                "PRETTY_NAME: " + os_release["values"].get("PRETTY_NAME", "Unavailable"),
                "ID: " + os_release["values"].get("ID", "Unavailable")
            ]
        },
        {
            "name": "IP addresses",
            "status": "ok" if addresses else "warn",
            "summary": ", ".join(addresses) if addresses else "No non-loopback IPv4 addresses found",
            "details": ["Collected from local hostname address resolution."]
        },
        {
            "name": "Client family",
            "status": "ok" if detection["confidence"] == "high" else "warn",
            "summary": detection["family"] + " (" + detection["confidence"] + " confidence)",
            "details": ["Based on local paths and /etc/os-release heuristics."]
        }
    ]
    return checks


def collect_status():
    os_release = read_os_release()
    detection = detect_client_family(os_release)
    addresses = get_ip_addresses()
    return {
        "timestamp": utc_now(),
        "agent": {
            "name": "client-readiness-agent",
            "version": "0.1.0",
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
        "checks": local_checks(os_release, addresses, detection)
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "ClientReadinessAgent/0.1"

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

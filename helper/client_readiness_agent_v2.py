#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import socket
import subprocess
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from pathlib import Path
from typing import Any


BASELINE_VERSION = "2026.04.17"


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


class CollectionError(RuntimeError):
    """A check could not collect evidence; this is not a client failure."""


def run_command(cmd: list[str], timeout: int = 10, allowed_codes=(0,)) -> str:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if result.returncode not in allowed_codes:
            raise CollectionError("Command exited with status %s" % result.returncode)
        return (result.stdout or "").strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CollectionError(type(exc).__name__) from exc


def check_online(host: str = "8.8.8.8", port: int = 53, timeout: float = 2.0) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
        return True
    except Exception:
        return False


def collect_capabilities() -> list[str]:
    capabilities = ["network.online", "network.hostname", "network.local_ips", "meta.profile", "meta.baseline_version"]
    system = platform.system()
    if system == "Darwin":
        capabilities.append("citrix.installed")
        if command_exists("defaults"):
            capabilities.append("citrix.version")
        if command_exists("security"):
            capabilities.extend(["certificates.installed", "certificates.details"])
    if command_exists("pgrep"):
        capabilities.extend(["processes.running", "processes.missing"])
    if system == "Linux" and (command_exists("systemctl") or command_exists("service")):
        capabilities.append("smartcard.pcscd_running")
    if system == "Linux" and command_exists("pcsc_scan"):
        capabilities.append("smartcard.readers")
    if system == "Linux" and command_exists("lsusb"):
        capabilities.append("smartcard.usb_devices")
    if command_exists("opensc-tool"):
        capabilities.append("smartcard.opensc_readers")
    if system == "Darwin" and command_exists("system_profiler"):
        capabilities.append("smartcard.system_profiler")
    return sorted(capabilities)


def collect_meta(profile_name: str) -> dict[str, Any]:
    return {
        "agent_version": "2.4.0",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "baseline_version": BASELINE_VERSION,
        "profile": profile_name,
        "platform": platform.system(),
        "platform_release": platform.release(),
        "machine": platform.machine(),
        "hostname": socket.gethostname(),
        "capabilities": collect_capabilities(),
    }


def _parse_security_certificate_text(text: str, store: str) -> list[dict[str, str]]:
    certs: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    sha1_re = re.compile(r"SHA-1 hash:\s*([A-Fa-f0-9]{40})")
    key_value_re = re.compile(r'^\s*"([^"]+)"<[^>]+>=(.*)$')

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        sha1_match = sha1_re.search(line)
        if sha1_match:
            if current:
                certs.append(current)
            current = {
                "thumbprint": sha1_match.group(1),
                "store": store,
            }
            continue

        kv_match = key_value_re.match(line)
        if kv_match and current is not None:
            key = kv_match.group(1).strip()
            value = kv_match.group(2).strip().strip('"')

            if key == "alis":
                current["name"] = value
            elif key == "labl":
                current.setdefault("name", value)
            elif key == "subj":
                current["subject"] = value
            elif key == "issr":
                current["issuer"] = value
            # cdat/mdat are keychain item timestamps, not X.509 validity.
            # No expiry claim is made without an actual certificate date.

    if current:
        certs.append(current)

    return certs


def collect_certificates() -> dict[str, Any]:
    details: list[dict[str, str]] = []

    if platform.system() == "Darwin" and command_exists("security"):
        keychain_sources = [
            (
                "/System/Library/Keychains/SystemRootCertificates.keychain",
                "system-root",
            ),
            ("/Library/Keychains/System.keychain", "system"),
        ]

        for keychain_path, store_name in keychain_sources:
            if Path(keychain_path).exists():
                output = run_command(
                    ["security", "find-certificate", "-a", "-Z", keychain_path],
                    timeout=20,
                )
                if output:
                    details.extend(_parse_security_certificate_text(output, store_name))

    installed = sorted(
        {
            item.get("name", "Unknown Certificate")
            for item in details
            if item.get("name")
        }
    )

    return {
        "installed": installed,
        "details": details,
    }


def collect_citrix() -> dict[str, Any]:
    app_candidates = [
        Path("/Applications/Citrix Workspace.app"),
        Path("/Applications/Citrix Viewer.app"),
    ]

    installed = any(path.exists() for path in app_candidates)
    version = "unknown"
    app_path = None

    for candidate in app_candidates:
        if candidate.exists():
            app_path = candidate
            break

    if app_path and platform.system() == "Darwin" and command_exists("defaults"):
        info_plist_base = str(app_path / "Contents" / "Info").replace(".plist", "")
        detected = run_command(
            ["defaults", "read", info_plist_base, "CFBundleShortVersionString"]
        )
        if detected:
            version = detected

    return {
        "installed": installed,
        "version": version,
        "path": str(app_path) if app_path else None,
    }


WATCHED_PROCESSES = [
    "pcscd",
    "wfica",
    "selfservice",
    "AuthManagerDaemon",
    "storebrowse",
    "ctxcwahelper",
    "igel",
    "rmagent",
]


def collect_processes() -> dict[str, Any]:
    running: list[str] = []
    missing: list[str] = []

    for name in WATCHED_PROCESSES:
        out = run_command(["pgrep", "-x", name], timeout=5, allowed_codes=(0, 1))
        if out:
            running.append(name)
        else:
            missing.append(name)

    return {"running": running, "missing": missing}


def collect_smartcard() -> dict[str, Any]:
    system = platform.system()
    result: dict[str, Any] = {
        "pcscd_running": None,
        "readers": [],
        "usb_devices": [],
        "card_present": None,
        "opensc_readers": [],
    }

    if system == "Linux":
        # PC/SC daemon status
        if command_exists("systemctl"):
            status_out = run_command(["systemctl", "is-active", "pcscd"], allowed_codes=(0, 3))
            result["pcscd_running"] = status_out == "active"
        elif command_exists("service"):
            status_out = run_command(["service", "pcscd", "status"], allowed_codes=(0, 3))
            result["pcscd_running"] = "running" in status_out.lower()

        # Readers via pcsc_scan (non-interactive, list only)
        if command_exists("pcsc_scan"):
            readers_out = run_command(["pcsc_scan", "-r"], timeout=5)
            if readers_out:
                result["readers"] = [
                    line.strip()
                    for line in readers_out.splitlines()
                    if line.strip() and not line.startswith("PC/SC device scanner")
                ]

        # USB devices (filter for common smartcard reader vendors)
        if command_exists("lsusb"):
            lsusb_out = run_command(["lsusb"])
            if lsusb_out:
                result["usb_devices"] = [
                    line.strip() for line in lsusb_out.splitlines() if line.strip()
                ]

        # OpenSC readers
        if command_exists("opensc-tool"):
            opensc_out = run_command(["opensc-tool", "--list-readers"], timeout=5)
            if opensc_out:
                result["opensc_readers"] = [
                    line.strip() for line in opensc_out.splitlines() if line.strip()
                ]

    elif system == "Darwin":
        # macOS: system_profiler gives full smartcard info
        if command_exists("system_profiler"):
            sp_out = run_command(
                ["system_profiler", "SPSmartCardsDataType"], timeout=15
            )
            if sp_out:
                result["system_profiler"] = sp_out

        # sc_auth: smartcard-to-user pairings
        if command_exists("sc_auth"):
            sc_out = run_command(["sc_auth", "list"], timeout=5)
            if sc_out:
                result["sc_auth_list"] = sc_out

        # OpenSC readers
        if command_exists("opensc-tool"):
            opensc_out = run_command(["opensc-tool", "--list-readers"], timeout=5)
            if opensc_out:
                result["opensc_readers"] = [
                    line.strip() for line in opensc_out.splitlines() if line.strip()
                ]

    return result


def collect_network() -> dict[str, Any]:
    local_ips: list[str] = []

    try:
        hostname = socket.gethostname()
        for result in socket.getaddrinfo(hostname, None):
            ip = result[4][0]
            if ":" not in ip and ip not in local_ips:
                local_ips.append(ip)
    except Exception:
        pass

    return {
        "online": check_online(),
        "hostname": socket.gethostname(),
        "local_ips": local_ips,
    }


def build_payload(profile_name: str) -> dict[str, Any]:
    meta = collect_meta(profile_name)
    payload = {"schema_version": "client-readiness.v2", "meta": meta}
    meta["collection_status"] = {}
    for category, collector in (
        ("certificates", collect_certificates), ("citrix", collect_citrix),
        ("network", collect_network), ("smartcard", collect_smartcard),
        ("processes", collect_processes),
    ):
        supported = any(c.startswith(category + ".") for c in meta["capabilities"])
        try:
            payload[category] = collector() if supported else {}
            status = "OK" if supported else "UNSUPPORTED"
            meta["collection_status"][category] = {"status": status}
        except CollectionError as exc:
            payload[category] = {}
            meta["collection_status"][category] = {"status": "ERROR", "detail": str(exc)}
    return payload


def make_handler(profile_name, allowed_origins):
    """Serve the v2 contract separately; the legacy v1 endpoint stays available."""
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            origin = self.headers.get("Origin")
            host = urlsplit("http://" + self.headers.get("Host", "")).hostname
            if host not in ("localhost", "127.0.0.1") or (origin and origin not in allowed_origins):
                self.send_error(403, "Host or origin not allowed")
                return
            path = urlsplit(self.path).path
            if path == "/health":
                payload = {"status": "ok", "schema_version": "client-readiness.v2"}
            elif path == "/status":
                payload = build_payload(profile_name)
            else:
                self.send_error(404)
                return
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            if origin:
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format_string, *args):
            return

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Client Readiness Agent v2")
    parser.add_argument(
        "--profile",
        default="macos-citrix",
        help="Profile ID to attach to helper output (default: macos-citrix)",
    )
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON output"
    )
    parser.add_argument("--out", help="Write JSON output to file")
    parser.add_argument("--serve", action="store_true", help="Serve the v2 contract on loopback")
    parser.add_argument("--port", type=int, default=38765)
    parser.add_argument("--allow-origin", action="append", default=[
        "https://mcamner.github.io", "http://localhost:8000", "http://127.0.0.1:8000"
    ])
    args = parser.parse_args()
    if args.serve:
        if args.out:
            parser.error("--out cannot be combined with --serve")
        with ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(args.profile, args.allow_origin)) as server:
            print("v2 helper listening on http://127.0.0.1:%s/status" % args.port, flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
        return

    payload = build_payload(args.profile)
    json_text = json.dumps(payload, indent=2 if args.pretty else None)

    if args.out:
        Path(args.out).write_text(json_text + "\n", encoding="utf-8")
    else:
        print(json_text)


if __name__ == "__main__":
    main()

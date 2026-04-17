#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import socket
import subprocess
from pathlib import Path
from typing import Any


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run_command(cmd: list[str], timeout: int = 10) -> str:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return (result.stdout or "").strip()
    except Exception:
        return ""


def check_online(host: str = "8.8.8.8", port: int = 53, timeout: float = 2.0) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
        return True
    except Exception:
        return False


def collect_meta() -> dict[str, Any]:
    return {
        "agent_version": "2.1.0",
        "platform": platform.system(),
        "platform_release": platform.release(),
        "machine": platform.machine(),
        "hostname": socket.gethostname(),
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
            elif key == "cdat":
                current["not_before"] = value
            elif key == "mdat":
                current["not_after"] = value

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
            (
                "/Library/Keychains/System.keychain",
                "system",
            ),
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


def build_payload() -> dict[str, Any]:
    return {
        "meta": collect_meta(),
        "certificates": collect_certificates(),
        "citrix": collect_citrix(),
        "network": collect_network(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Client Readiness Agent v2")
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON output"
    )
    parser.add_argument("--out", help="Write JSON output to file")
    args = parser.parse_args()

    payload = build_payload()
    json_text = json.dumps(payload, indent=2 if args.pretty else None)

    if args.out:
        Path(args.out).write_text(json_text + "\n", encoding="utf-8")
    else:
        print(json_text)


if __name__ == "__main__":
    main()

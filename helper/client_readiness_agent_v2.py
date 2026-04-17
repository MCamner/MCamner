#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
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
        "agent_version": "2.0.0",
        "platform": platform.system(),
        "platform_release": platform.release(),
        "machine": platform.machine(),
        "hostname": socket.gethostname(),
    }


def collect_certificates() -> dict[str, Any]:
    installed: list[str] = []
    details: list[dict[str, str]] = []

    if platform.system() == "Darwin" and command_exists("security"):
        # Enkel och robust startpunkt.
        # Nästa nivå blir att parsa subject/issuer/expiry mer exakt.
        output = run_command(
            [
                "security",
                "find-certificate",
                "-a",
                "-Z",
                "/System/Library/Keychains/SystemRootCertificates.keychain",
            ]
        )

        if output:
            for line in output.splitlines():
                line = line.strip()
                if '"alis"' in line:
                    # Exempelrad innehåller ofta aliasnamn
                    name = line.split("<blob>=")[-1].strip().strip('"')
                    if name:
                        installed.append(name)
                        details.append({"name": name, "store": "system-root"})

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
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    parser.add_argument(
        "--out",
        help="Write JSON output to file",
    )
    args = parser.parse_args()

    payload = build_payload()
    json_text = json.dumps(payload, indent=2 if args.pretty else None)

    if args.out:
        Path(args.out).write_text(json_text + "\n", encoding="utf-8")
    else:
        print(json_text)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import os
import platform
import socket
import subprocess
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


HOST = "127.0.0.1"
PORT = 38765


CERT_SEARCH_PATHS = [
    "/etc/ssl/certs",
    "/etc/pki/tls/certs",
    "/usr/local/share/ca-certificates",
    "/etc/ca-certificates",
    os.path.expanduser("~/.pki"),
    os.path.expanduser("~/.config"),
]


def run_command(cmd):
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=8, check=False
        )
        return {
            "ok": result.returncode == 0,
            "stdout": (result.stdout or "").strip(),
            "stderr": (result.stderr or "").strip(),
            "returncode": result.returncode,
        }
    except Exception as e:
        return {"ok": False, "stdout": "", "stderr": str(e), "returncode": -1}


def get_ip_addresses():
    ips = []
    try:
        hostname = socket.gethostname()
        for item in socket.getaddrinfo(hostname, None):
            addr = item[4][0]
            if ":" not in addr and not addr.startswith("127.") and addr not in ips:
                ips.append(addr)
    except Exception:
        pass
    return ips


def get_default_gateway_linux():
    result = run_command(["sh", "-c", "ip route | awk '/default/ {print $3; exit}'"])
    return result["stdout"] if result["ok"] and result["stdout"] else ""


def get_active_interface_linux():
    result = run_command(["sh", "-c", "ip route | awk '/default/ {print $5; exit}'"])
    return result["stdout"] if result["ok"] and result["stdout"] else ""


def get_dns_servers_linux():
    servers = []
    try:
        with open("/etc/resolv.conf", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("nameserver "):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] not in servers:
                        servers.append(parts[1])
    except Exception:
        pass
    return servers


def get_wifi_ssid_linux():
    result = run_command(["sh", "-c", "iwgetid -r 2>/dev/null || true"])
    if result["stdout"]:
        return result["stdout"]

    result = run_command(
        [
            "sh",
            "-c",
            "nmcli -t -f active,ssid dev wifi 2>/dev/null | awk -F: '$1==\"yes\" {print $2; exit}'",
        ]
    )
    if result["stdout"]:
        return result["stdout"]

    return ""


def classify_interface(name):
    if not name:
        return "unknown"
    lowered = name.lower()
    if lowered.startswith(("wlan", "wifi", "wl")):
        return "wifi"
    if lowered.startswith(("eth", "en")):
        return "lan"
    return "other"


def get_network_info():
    system = platform.system().lower()

    info = {
        "lan_connected": False,
        "wifi_enabled": False,
        "wifi_connected": False,
        "ssid": "",
        "active_interface": "",
        "interface_type": "unknown",
        "ip_addresses": [],
        "default_gateway": "",
        "dns_servers": [],
        "notes": [],
    }

    info["ip_addresses"] = get_ip_addresses()

    if system == "linux":
        active_interface = get_active_interface_linux()
        gateway = get_default_gateway_linux()
        dns_servers = get_dns_servers_linux()
        ssid = get_wifi_ssid_linux()
        interface_type = classify_interface(active_interface)

        info["active_interface"] = active_interface
        info["interface_type"] = interface_type
        info["default_gateway"] = gateway
        info["dns_servers"] = dns_servers
        info["ssid"] = ssid

        info["wifi_connected"] = bool(ssid)
        info["wifi_enabled"] = bool(ssid or interface_type == "wifi")
        info["lan_connected"] = interface_type == "lan" and bool(info["ip_addresses"])

        if interface_type == "wifi" and bool(info["ip_addresses"]):
            info["notes"].append("Active connection appears to use Wi-Fi.")
        elif interface_type == "lan" and bool(info["ip_addresses"]):
            info["notes"].append("Active connection appears to use wired LAN.")
        else:
            info["notes"].append(
                "Active network type could not be determined with high confidence."
            )

        if not gateway:
            info["notes"].append("Default gateway was not detected.")
        if not dns_servers:
            info["notes"].append("No DNS servers were detected from resolv.conf.")
    else:
        info["notes"].append(
            f"Network inspection is not implemented yet for {platform.system()}."
        )

    return info


def parse_openssl_date(value):
    try:
        parsed = datetime.strptime(value.strip(), "%b %d %H:%M:%S %Y %Z")
        return parsed.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def classify_certificate(subject, issuer, extended_usage, path):
    combined = " ".join(
        [subject or "", issuer or "", " ".join(extended_usage or []), path or ""]
    ).lower()

    has_client_auth = (
        "client auth" in combined or "tls web client authentication" in combined
    )
    has_smartcard_logon = "smartcard" in combined or "smart card" in combined
    source = "system"

    lowered_path = (path or "").lower()
    if (
        "/home/" in lowered_path
        or "/.pki" in lowered_path
        or "/.config" in lowered_path
    ):
        source = "user"

    return {
        "has_client_auth": has_client_auth,
        "has_smartcard_logon": has_smartcard_logon,
        "source": source,
    }


def extract_certificate_info(path):
    subject_res = run_command(["openssl", "x509", "-in", path, "-noout", "-subject"])
    issuer_res = run_command(["openssl", "x509", "-in", path, "-noout", "-issuer"])
    start_res = run_command(["openssl", "x509", "-in", path, "-noout", "-startdate"])
    end_res = run_command(["openssl", "x509", "-in", path, "-noout", "-enddate"])
    serial_res = run_command(["openssl", "x509", "-in", path, "-noout", "-serial"])
    fp_res = run_command(
        ["openssl", "x509", "-in", path, "-noout", "-fingerprint", "-sha256"]
    )
    text_res = run_command(["openssl", "x509", "-in", path, "-noout", "-text"])

    if not subject_res["ok"]:
        return None

    subject = subject_res["stdout"].replace("subject=", "", 1).strip()
    issuer = (
        issuer_res["stdout"].replace("issuer=", "", 1).strip()
        if issuer_res["ok"]
        else ""
    )
    valid_from_raw = (
        start_res["stdout"].replace("notBefore=", "", 1).strip()
        if start_res["ok"]
        else ""
    )
    valid_to_raw = (
        end_res["stdout"].replace("notAfter=", "", 1).strip() if end_res["ok"] else ""
    )
    serial = (
        serial_res["stdout"].replace("serial=", "", 1).strip()
        if serial_res["ok"]
        else ""
    )
    thumbprint = (
        fp_res["stdout"].split("=", 1)[1].strip()
        if fp_res["ok"] and "=" in fp_res["stdout"]
        else ""
    )

    extended_usage = []
    text_blob = text_res["stdout"] if text_res["ok"] else ""
    if "Extended Key Usage" in text_blob:
        lines = text_blob.splitlines()
        for idx, line in enumerate(lines):
            if "Extended Key Usage" in line and idx + 1 < len(lines):
                next_line = lines[idx + 1].strip()
                if next_line:
                    extended_usage = [
                        item.strip() for item in next_line.split(",") if item.strip()
                    ]
                break

    valid_to_dt = parse_openssl_date(valid_to_raw)
    now = datetime.now(timezone.utc)
    expired = bool(valid_to_dt and valid_to_dt < now)
    expires_soon = bool(valid_to_dt and not expired and (valid_to_dt - now).days <= 30)

    flags = classify_certificate(subject, issuer, extended_usage, path)

    return {
        "path": path,
        "subject": subject,
        "issuer": issuer,
        "valid_from": valid_from_raw,
        "valid_to": valid_to_raw,
        "serial": serial,
        "thumbprint": thumbprint,
        "extended_usage": extended_usage,
        "expired": expired,
        "expires_soon": expires_soon,
        "has_client_auth": flags["has_client_auth"],
        "has_smartcard_logon": flags["has_smartcard_logon"],
        "source": flags["source"],
    }


def find_certificate_files():
    files = []
    seen = set()
    for base in CERT_SEARCH_PATHS:
        if not os.path.exists(base):
            continue
        if os.path.isfile(base):
            candidates = [base]
        else:
            candidates = []
            for root, _, names in os.walk(base):
                for name in names:
                    lowered = name.lower()
                    if lowered.endswith((".crt", ".cer", ".pem")):
                        candidates.append(os.path.join(root, name))
        for path in candidates:
            if path not in seen:
                seen.add(path)
                files.append(path)
    return files


def get_certificates():
    openssl_check = run_command(["openssl", "version"])
    if not openssl_check["ok"]:
        return {
            "store_available": False,
            "certificates": [],
            "notes": [
                "OpenSSL is not available, so certificate inspection could not run."
            ],
        }

    found_files = find_certificate_files()
    certificates = []

    for path in found_files[:200]:
        info = extract_certificate_info(path)
        if info:
            certificates.append(info)

    client_auth_count = sum(1 for c in certificates if c.get("has_client_auth"))
    smartcard_count = sum(1 for c in certificates if c.get("has_smartcard_logon"))
    expired_count = sum(1 for c in certificates if c.get("expired"))
    soon_count = sum(1 for c in certificates if c.get("expires_soon"))

    notes = [
        f"OpenSSL certificate scan completed across {len(found_files)} candidate files.",
        "This version scans readable certificate files and does not yet inspect PKCS#11 token stores.",
    ]

    if not certificates:
        notes.append(
            "No readable certificate files were found in the configured search paths."
        )
    if expired_count:
        notes.append(f"{expired_count} certificate(s) appear to be expired.")
    if soon_count:
        notes.append(f"{soon_count} certificate(s) expire within 30 days.")
    if client_auth_count == 0:
        notes.append(
            "No obvious client-auth certificate was identified in the scanned files."
        )

    return {
        "store_available": True,
        "search_paths": CERT_SEARCH_PATHS,
        "candidate_files": len(found_files),
        "certificates": certificates,
        "summary": {
            "total": len(certificates),
            "client_auth": client_auth_count,
            "smartcard_logon": smartcard_count,
            "expired": expired_count,
            "expires_soon": soon_count,
        },
        "notes": notes,
    }


def get_smartcard():
    return {
        "reader_present": False,
        "card_inserted": False,
        "middleware_detected": False,
        "reader_name": "",
        "card_label": "",
        "cert_count": 0,
        "status": "not_implemented",
        "notes": [
            "Smartcard inspection is not implemented yet.",
            "Next step: add PC/SC reader detection and card enumeration.",
        ],
    }


def build_status_payload(baseline_name=""):
    return {
        "agent": {"name": "client-helper", "version": "0.3.0"},
        "hostname": socket.gethostname(),
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
        },
        "baseline": {"name": baseline_name or "Default"},
        "client_detection": {"family": f"{platform.system()} host"},
        "categories": {
            "host": {"status": "ok"},
            "network": {"status": "ok"},
            "certificates": {"status": "ok"},
            "smartcard": {"status": "warn"},
        },
        "checks": [
            {
                "name": "Network summary",
                "status": "ok",
                "summary": "Helper can provide host-level network data.",
                "details": [
                    "Use /network for interface, IP, gateway, DNS, and Wi-Fi summary."
                ],
            },
            {
                "name": "Certificates",
                "status": "ok",
                "summary": "Certificate scanning is available.",
                "details": [
                    "Use /certificates for scanned PEM/CRT/CER certificate summaries."
                ],
            },
            {
                "name": "Smartcard",
                "status": "warn",
                "summary": "Smartcard inspection not implemented yet.",
                "details": ["Use /smartcard after PC/SC integration is implemented."],
            },
        ],
    }


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        baseline = query.get("baseline", [""])[0]

        if parsed.path == "/status":
            self._send_json(build_status_payload(baseline))
            return

        if parsed.path == "/network":
            self._send_json(get_network_info())
            return

        if parsed.path == "/certificates":
            self._send_json(get_certificates())
            return

        if parsed.path == "/smartcard":
            self._send_json(get_smartcard())
            return

        self._send_json(
            {
                "error": "not_found",
                "available_endpoints": [
                    "/status",
                    "/network",
                    "/certificates",
                    "/smartcard",
                ],
            },
            status=404,
        )

    def log_message(self, fmt, *args):
        return


def main():
    server = HTTPServer((HOST, PORT), Handler)
    print(f"client-helper listening on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import platform
import socket
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


HOST = "127.0.0.1"
PORT = 38765


def run_command(cmd):
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        return {
            "ok": result.returncode == 0,
            "stdout": (result.stdout or "").strip(),
            "stderr": (result.stderr or "").strip(),
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "ok": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }


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
    # Try iwgetid first
    result = run_command(["sh", "-c", "iwgetid -r 2>/dev/null || true"])
    if result["stdout"]:
        return result["stdout"]

    # Fallback: nmcli if available
    result = run_command([
        "sh", "-c",
        "nmcli -t -f active,ssid dev wifi 2>/dev/null | awk -F: '$1==\"yes\" {print $2; exit}'"
    ])
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
        "notes": []
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
            info["notes"].append("Active network type could not be determined with high confidence.")

        if not gateway:
            info["notes"].append("Default gateway was not detected.")
        if not dns_servers:
            info["notes"].append("No DNS servers were detected from resolv.conf.")
    else:
        info["notes"].append(f"Network inspection is not implemented yet for {platform.system()}.")

    return info


def get_certificates():
    return {
        "store_available": False,
        "certificates": [],
        "notes": [
            "Certificate inspection is not implemented yet.",
            "Next step: add OS12/Linux certificate enumeration."
        ]
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
            "Next step: add PC/SC reader detection and card enumeration."
        ]
    }


def build_status_payload(baseline_name=""):
    return {
        "agent": {
          "name": "client-helper",
          "version": "0.2.0"
        },
        "hostname": socket.gethostname(),
        "os": {
          "system": platform.system(),
          "release": platform.release(),
          "version": platform.version(),
          "machine": platform.machine()
        },
        "baseline": {
          "name": baseline_name or "Default"
        },
        "client_detection": {
          "family": f"{platform.system()} host"
        },
        "categories": {
          "host": {"status": "ok"},
          "network": {"status": "ok"},
          "certificates": {"status": "warn"},
          "smartcard": {"status": "warn"}
        },
        "checks": [
          {
            "name": "Network summary",
            "status": "ok",
            "summary": "Helper can provide host-level network data.",
            "details": [
              "Use /network for interface, IP, gateway, DNS, and Wi-Fi summary."
            ]
          },
          {
            "name": "Certificates",
            "status": "warn",
            "summary": "Certificate inspection not implemented yet.",
            "details": [
              "Use /certificates after certificate enumeration is implemented."
            ]
          },
          {
            "name": "Smartcard",
            "status": "warn",
            "summary": "Smartcard inspection not implemented yet.",
            "details": [
              "Use /smartcard after PC/SC integration is implemented."
            ]
          }
        ]
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

        self._send_json({
            "error": "not_found",
            "available_endpoints": [
                "/status",
                "/network",
                "/certificates",
                "/smartcard"
            ]
        }, status=404)

    def log_message(self, fmt, *args):
        return


def main():
    server = HTTPServer((HOST, PORT), Handler)
    print(f"client-helper listening on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()

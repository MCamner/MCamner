#!/bin/sh

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

exec /usr/bin/python3 "$SCRIPT_DIR/client_readiness_agent.py" --baseline macos-citrix

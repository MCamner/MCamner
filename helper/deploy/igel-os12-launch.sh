#!/bin/sh

# Suggested IGEL OS 12 launcher example
# Place the helper under:
#   /custom/client-readiness/
#
# Example command for a custom application:
#   /usr/bin/python3 /custom/client-readiness/client_readiness_agent.py --baseline igel-os12

exec /usr/bin/python3 /custom/client-readiness/client_readiness_agent.py --baseline igel-os12

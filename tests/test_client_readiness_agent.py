import json
import os
import tempfile
import threading
import urllib.error
import urllib.request

import pytest

from helper.client_readiness_agent import (
    BASELINES_DIR,
    DEFAULT_BASELINE_PATH,
    Handler,
    collapse_status,
    read_json_file,
    resolve_baseline_path,
    status_priority,
)
from http.server import ThreadingHTTPServer


def test_status_priority():
    assert status_priority("fail") == 0
    assert status_priority("warn") == 1
    assert status_priority("ok") == 2
    assert status_priority("unknown") == 1


def test_collapse_status():
    assert collapse_status(["ok", "ok"]) == "ok"
    assert collapse_status(["ok", "warn"]) == "warn"
    assert collapse_status(["fail", "ok"]) == "fail"
    assert collapse_status(["warn", "fail", "ok"]) == "fail"


def test_read_json_file():
    # Create a temporary JSON file
    test_data = {"key": "value"}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(test_data, f)
        temp_path = f.name

    try:
        result = read_json_file(temp_path)
        assert result["available"] is True
        assert result["values"] == test_data
    finally:
        os.unlink(temp_path)

    # Test non-existent file
    result = read_json_file("nonexistent.json")
    assert result["available"] is False
    assert result["values"] == {}


def test_read_json_file_malformed():
    # A file that exists but does not contain valid JSON must fail closed
    # rather than raising, since callers treat "available" as the only gate.
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{not valid json,,,")
        temp_path = f.name

    try:
        result = read_json_file(temp_path)
        assert result["available"] is False
        assert result["values"] == {}
        assert result["path"] == temp_path
    finally:
        os.unlink(temp_path)


def test_read_json_file_empty_file():
    # An empty file is a common "half-written config" case and should also
    # fail closed instead of raising json.JSONDecodeError.
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        result = read_json_file(temp_path)
        assert result["available"] is False
        assert result["values"] == {}
    finally:
        os.unlink(temp_path)


def test_resolve_baseline_path_defaults_when_no_name():
    assert resolve_baseline_path(None) == DEFAULT_BASELINE_PATH
    assert resolve_baseline_path("") == DEFAULT_BASELINE_PATH


def test_resolve_baseline_path_known_names():
    for name in ("igel-os12", "elux7"):
        expected = os.path.join(BASELINES_DIR, name + ".json")
        assert os.path.exists(expected), f"fixture baseline missing: {expected}"
        assert resolve_baseline_path(name) == expected


def test_resolve_baseline_path_unknown_name_falls_back_to_default():
    # An unrecognized baseline name must not error; it should fall back to
    # the generic default rather than pointing at a non-existent file.
    assert resolve_baseline_path("does-not-exist") == DEFAULT_BASELINE_PATH


def test_resolve_baseline_path_rejects_path_traversal():
    # A crafted name with path separators must not escape BASELINES_DIR.
    # os.path.basename() strips the directory components first, so this
    # should resolve like an unknown name (fall back to default) instead of
    # reading an arbitrary file such as /etc/passwd.
    traversal = "../../../../etc/passwd"
    resolved = resolve_baseline_path(traversal)
    assert resolved == DEFAULT_BASELINE_PATH
    assert os.path.commonpath(
        [os.path.abspath(resolved), os.path.abspath(BASELINES_DIR)]
    ) == os.path.commonpath(
        [os.path.abspath(DEFAULT_BASELINE_PATH), os.path.abspath(BASELINES_DIR)]
    )


@pytest.fixture()
def running_agent_server():
    # Bind to an ephemeral port (0) so the test never collides with a real
    # agent instance a developer might have running on the default port.
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _get_json(url):
    with urllib.request.urlopen(url, timeout=5) as response:
        return response, json.loads(response.read().decode("utf-8"))


def test_health_endpoint_contract(running_agent_server):
    response, payload = _get_json(running_agent_server + "/health")
    assert response.status == 200
    assert response.headers.get("Content-Type", "").startswith("application/json")
    assert payload["status"] == "ok"
    assert "timestamp" in payload


def test_status_endpoint_contract(running_agent_server):
    response, payload = _get_json(running_agent_server + "/status")
    assert response.status == 200
    assert response.headers.get("Content-Type", "").startswith("application/json")
    assert response.headers.get("Access-Control-Allow-Origin") == "*"

    # The browser page depends on this exact top-level shape; a breaking
    # rename here would silently strand the client-readiness UI.
    for key in (
        "timestamp",
        "agent",
        "hostname",
        "platform",
        "baseline",
        "available_baselines",
        "overall_status",
        "categories",
        "checks",
    ):
        assert key in payload, f"missing top-level key: {key}"

    assert payload["overall_status"] in ("ok", "warn", "fail")
    assert isinstance(payload["checks"], list) and payload["checks"]


def test_status_endpoint_unknown_baseline_falls_back(running_agent_server):
    # Requesting a baseline name that doesn't exist must not error out; the
    # handler should serve the default baseline instead (same contract as
    # resolve_baseline_path's fallback behavior, exercised over HTTP).
    response, payload = _get_json(
        running_agent_server + "/status?baseline=totally-unknown-profile"
    )
    assert response.status == 200
    assert payload["baseline"]["path"] == DEFAULT_BASELINE_PATH


def test_unknown_path_returns_404(running_agent_server):
    try:
        urllib.request.urlopen(running_agent_server + "/nope", timeout=5)
        assert False, "expected HTTPError for unmapped path"
    except urllib.error.HTTPError as exc:
        assert exc.code == 404
        payload = json.loads(exc.read().decode("utf-8"))
        assert payload["error"] == "Not found"

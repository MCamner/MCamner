import tempfile
import json
import os
from helper.client_readiness_agent import (
    status_priority,
    collapse_status,
    read_json_file,
)


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

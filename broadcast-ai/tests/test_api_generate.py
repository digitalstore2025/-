"""
Tests for /api/generate endpoint response structure.

Validates the standardized response envelope introduced in commit 90b0fbe:
  Success: {"success": true, "data": {"path": str, "duration": float, "style": str}}
  Error:   {"success": false, "error": str}
"""

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Minimal stubs so tv_server.py can be imported without heavy dependencies
# ---------------------------------------------------------------------------

_broadcast_ai_dir = Path(__file__).resolve().parent.parent

# Stub out 'config' so OUTPUT_DIR and SERVER_* are available
_config_stub = types.ModuleType("config")
_config_stub.OUTPUT_DIR = Path("/tmp/broadcast_ai_test_output")
_config_stub.SERVER_HOST = "127.0.0.1"
_config_stub.SERVER_PORT = 5000
sys.modules.setdefault("config", _config_stub)

# Stub out 'logger'
_logger_stub = types.ModuleType("logger")
_logger_stub.get_logger = lambda name: MagicMock()
sys.modules.setdefault("logger", _logger_stub)

# Stub out 'scheduler'
_scheduler_stub = types.ModuleType("scheduler")
_scheduler_stub.get_current_block = lambda: "news"
_scheduler_stub.get_next_block_change = lambda: {
    "current_label": "أخبار",
    "next_label": "قرآن",
    "minutes_until": 30,
}
_scheduler_stub.get_schedule_display = lambda: []
sys.modules.setdefault("scheduler", _scheduler_stub)

# Now import the Flask app
sys.path.insert(0, str(_broadcast_ai_dir))
from tv_server import app  # noqa: E402


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Missing or invalid request body
# ---------------------------------------------------------------------------

class TestApiGenerateBadRequest:
    def test_missing_body_returns_failure_envelope(self, client):
        rv = client.post("/api/generate", content_type="application/json", data="")
        assert rv.status_code == 400
        body = rv.get_json()
        assert body["success"] is False
        assert "error" in body

    def test_missing_text_field_returns_failure_envelope(self, client):
        rv = client.post("/api/generate", json={"style": "news"})
        assert rv.status_code == 400
        body = rv.get_json()
        assert body["success"] is False
        assert "error" in body
        # No legacy bare 'path' key should be present
        assert "path" not in body

    def test_path_traversal_in_output_name_returns_failure_envelope(self, client):
        rv = client.post("/api/generate", json={"text": "hello", "output": "../evil.wav"})
        assert rv.status_code == 400
        body = rv.get_json()
        assert body["success"] is False
        assert "error" in body

    def test_backslash_in_output_name_returns_failure_envelope(self, client):
        rv = client.post("/api/generate", json={"text": "hello", "output": "sub\\evil.wav"})
        assert rv.status_code == 400
        body = rv.get_json()
        assert body["success"] is False
        assert "error" in body


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_generate_module(return_value=None, side_effect=None):
    """Return a stub *generate* module for use with patch.dict(sys.modules).

    tv_server.py imports generate lazily inside the function body
    (``from generate import generate_voice``), so the correct way to
    intercept this is via sys.modules rather than patching a module-level
    attribute.
    """
    stub = types.ModuleType("generate")
    mock_fn = MagicMock(return_value=return_value, side_effect=side_effect)
    stub.generate_voice = mock_fn
    return stub


# ---------------------------------------------------------------------------
# Successful generation
# ---------------------------------------------------------------------------

class TestApiGenerateSuccess:
    def test_success_returns_envelope_with_data(self, client):
        fake_path = "/tmp/broadcast_ai_test_output/api_test.wav"
        with patch.dict("sys.modules", {"generate": _make_generate_module(return_value=fake_path)}):
            rv = client.post("/api/generate", json={"text": "مرحبا", "style": "news"})
        assert rv.status_code == 200
        body = rv.get_json()
        assert body["success"] is True
        assert "data" in body
        data = body["data"]
        assert data["path"] == fake_path
        assert "duration" in data
        assert data["style"] == "news"
        # No bare 'path' at top level (old format)
        assert "path" not in body

    def test_success_default_style_is_news(self, client):
        fake_path = "/tmp/broadcast_ai_test_output/api_test.wav"
        with patch.dict("sys.modules", {"generate": _make_generate_module(return_value=fake_path)}):
            rv = client.post("/api/generate", json={"text": "مرحبا"})
        assert rv.status_code == 200
        body = rv.get_json()
        assert body["success"] is True
        assert body["data"]["style"] == "news"


# ---------------------------------------------------------------------------
# Generation error (e.g. model not available)
# ---------------------------------------------------------------------------

class TestApiGenerateInternalError:
    def test_generation_exception_returns_failure_envelope(self, client):
        with patch.dict(
            "sys.modules",
            {"generate": _make_generate_module(side_effect=RuntimeError("model not loaded"))},
        ):
            rv = client.post("/api/generate", json={"text": "مرحبا"})
        assert rv.status_code == 500
        body = rv.get_json()
        assert body["success"] is False
        assert "model not loaded" in body["error"]
        assert "data" not in body

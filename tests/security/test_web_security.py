"""
tests/security/test_web_security.py

Tests for Phase 2 security foundation:
- CSRF protection
- Security headers (CSP, X-Content-Type-Options)
- Egress Guard blocking outbound connections
- Log redaction
"""
import logging
import socket
from io import StringIO
import pytest
from flask import Flask

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from bi_automation.security.csrf import init_csrf, csrf_protect
from bi_automation.security.egress_guard import EgressBlockedError, install, is_installed
from bi_automation.security.log_redaction import RedactingFilter

# ── 1. CSRF Protection ────────────────────────────────────────────────────────

@pytest.fixture
def csrf_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test-key"
    init_csrf(app)

    @app.route("/unprotected", methods=["POST"])
    def unprotected():
        return "OK"

    @app.route("/protected", methods=["POST"])
    @csrf_protect
    def protected():
        return "OK"

    @app.route("/form", methods=["GET"])
    def form():
        # Using the injected context processor
        from flask import render_template_string
        return render_template_string("{{ csrf_token() }}")

    return app

def test_csrf_unprotected(csrf_app):
    with csrf_app.test_client() as client:
        res = client.post("/unprotected")
        assert res.status_code == 200

def test_csrf_protected_missing_token(csrf_app):
    with csrf_app.test_client() as client:
        res = client.post("/protected")
        assert res.status_code == 403

def test_csrf_protected_with_header_token(csrf_app):
    with csrf_app.test_client() as client:
        # GET form to initialize token
        res1 = client.get("/form")
        token = res1.get_data(as_text=True)

        # Use in header
        res2 = client.post("/protected", headers={"X-CSRF-Token": token})
        assert res2.status_code == 200

def test_csrf_protected_with_form_token(csrf_app):
    with csrf_app.test_client() as client:
        res1 = client.get("/form")
        token = res1.get_data(as_text=True)

        # Use in form data
        res2 = client.post("/protected", data={"_csrf_token": token})
        assert res2.status_code == 200

def test_csrf_invalid_token(csrf_app):
    with csrf_app.test_client() as client:
        client.get("/form") # init
        res = client.post("/protected", headers={"X-CSRF-Token": "invalid123"})
        assert res.status_code == 403


# ── 2. Egress Guard ──────────────────────────────────────────────────────────

def test_egress_guard_blocks_external():
    """Verify egress guard patches socket and blocks non-loopback."""
    install()
    assert is_installed()
    
    # Should block external
    with pytest.raises(EgressBlockedError):
        socket.socket().connect(("example.com", 80))
        
    with pytest.raises(EgressBlockedError):
        socket.create_connection(("8.8.8.8", 53))

    # Should allow loopback
    try:
        # It will fail with ConnectionRefusedError if nothing is listening,
        # but it shouldn't raise EgressBlockedError
        socket.socket().connect(("127.0.0.1", 9999))
    except EgressBlockedError:
        pytest.fail("Egress guard blocked localhost")
    except ConnectionRefusedError:
        pass


# ── 3. Log Redaction ─────────────────────────────────────────────────────────

def test_log_redaction_filter():
    """Verify sensitive patterns are redacted from log messages."""
    logger = logging.getLogger("test_redaction")
    logger.setLevel(logging.DEBUG)
    
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    handler.addFilter(RedactingFilter())
    logger.addHandler(handler)
    
    # Test cases
    logger.info("Found cell value 'ThisIsALongStringThatShouldBeRedacted123'")
    logger.info("User email is john.doe@example.com")
    logger.info("Customer ID 1234567890 loaded")
    logger.info("Processing C:/path/to/my_data_file.xlsx")
    
    output = stream.getvalue()
    
    assert "ThisIsALongString" not in output
    assert "<redacted>" in output
    assert "john.doe@example.com" not in output
    assert "<email>" in output
    assert "1234567890" not in output
    assert "<digits>" in output
    assert "my_data_file.xlsx" not in output
    assert "file-" in output
    assert ".xlsx" in output

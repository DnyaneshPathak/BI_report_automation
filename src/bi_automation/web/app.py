"""
src/bi_automation/web/app.py
Flask application factory — create_app() + run().

Imports existing route logic from the legacy flask_app.py and
wires it through the new security-hardened factory.
Phase 2 will add CSRF, egress guard, CSP headers, etc.
This phase keeps everything working while the src/ structure is in place.
"""
from __future__ import annotations

import logging
import logging.handlers
import sys
import os
from pathlib import Path

# ── Ensure src/ is importable (needed when running main.py as a script) ───────
_src = Path(__file__).resolve().parents[3]  # project_root/src
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from flask import Flask

from bi_automation.config.settings import (
    SECRET_KEY, FLASK_HOST, FLASK_PORT,
    LOG_FILE, LOG_MAX_BYTES, LOG_BACKUP_COUNT, LOG_LEVEL,
    TEMP_DIR, OUTPUT_DIR,
)

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
def _configure_logging() -> None:
    root = logging.getLogger()
    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Rotating file handler in var/logs/
    fh = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    fh.setFormatter(fmt)
    root.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    # Attach the redacting filter to all root handlers
    from bi_automation.security.log_redaction import install_on_root
    install_on_root()


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
def create_app() -> Flask:
    """Create and configure the Flask application."""
    _configure_logging()

    # Ensure runtime dirs exist
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Start the TTL session reaper
    from bi_automation.security.temp_store import start_reaper
    start_reaper()

    # ── Import the legacy controller (which contains all current routes) ─────
    _project_root = Path(__file__).resolve().parents[3]
    if str(_project_root) not in sys.path:
        sys.path.insert(0, str(_project_root))

    # Import the legacy app object
    from bi_automation.web.routes.legacy_routes import app as legacy_app  # type: ignore
    from flask import request, abort

    # Overwrite the secret key with the secure one from settings
    legacy_app.secret_key = SECRET_KEY
    legacy_app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024
    legacy_app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    legacy_app.config["SESSION_COOKIE_HTTPONLY"] = True
    legacy_app.config["SESSION_COOKIE_SECURE"] = False  # Localhost only

    # ── Security Middleware ──────────────────────────────────────────────────

    # Host header check (mitigates DNS rebinding)
    @legacy_app.before_request
    def enforce_host_header():
        allowed_hosts = {f"127.0.0.1:{FLASK_PORT}", f"localhost:{FLASK_PORT}", "127.0.0.1", "localhost"}
        if request.host not in allowed_hosts:
            logger.warning("Rejected request with invalid Host header: %s", request.host)
            abort(400, description="Invalid Host header.")

    # Security response headers
    @legacy_app.after_request
    def add_security_headers(response):
        # Strict CSP: no inline scripts, everything from 'self'
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: blob:; "
            "script-src 'self' 'unsafe-inline'; " # TEMPORARY: allow inline until Phase 4 JS move
            "style-src 'self' 'unsafe-inline'; "  # TEMPORARY: allow inline until Phase 4 CSS move
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        
        # Don't cache data pages or API responses
        if request.path.startswith("/api/") or request.path in ("/preview", "/analyze"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            
        return response

    # Initialize CSRF protection (adds csrf_token() to templates)
    from bi_automation.security.csrf import init_csrf
    init_csrf(legacy_app)

    # Define the delete session endpoint here temporarily
    from bi_automation.security.temp_store import delete_session
    @legacy_app.route("/api/delete/<session_id>", methods=["DELETE", "POST"])
    def delete_session_endpoint(session_id):
        # Using POST as fallback for basic HTML forms if needed
        deleted = delete_session(session_id)
        return {"success": True, "deleted": deleted}, 200

    logger.info("BI Report Automation v2 — app factory ready")
    return legacy_app


# ---------------------------------------------------------------------------
# run() — called by main.py
# ---------------------------------------------------------------------------
def run() -> None:
    """Entry point: configure and start the Flask development server."""
    _configure_logging()

    logger.info("=" * 60)
    logger.info("BI Report Automation v2 — Starting")
    logger.info("URL: http://%s:%s", FLASK_HOST, FLASK_PORT)
    logger.info("All data processing is LOCAL. No external connections.")
    logger.info("=" * 60)

    # Egress guard installation
    from bi_automation.security.egress_guard import install, audit_report
    install()
    status_report = audit_report()
    logger.info("Privacy status: %s", status_report["status"])

    app = create_app()
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)

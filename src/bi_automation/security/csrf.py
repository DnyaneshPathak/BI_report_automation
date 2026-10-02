"""
src/bi_automation/security/csrf.py

CSRF protection using the Double-Submit Cookie pattern.
- A CSRF token is stored in the Flask session (server-side)
- Every state-changing POST must include the token as:
    - X-CSRF-Token header (for fetch/AJAX calls), OR
    - _csrf_token form field (for multipart form uploads)
- A Jinja2 context processor injects `csrf_token()` for templates

Usage:
    from bi_automation.security.csrf import init_csrf, csrf_protect
    init_csrf(app)

    @app.route("/analyze", methods=["POST"])
    @csrf_protect
    def analyze(): ...
"""
from __future__ import annotations

import functools
import logging
import secrets
from typing import Callable

from flask import Flask, abort, request, session

logger = logging.getLogger(__name__)

_TOKEN_KEY = "_csrf_token"
_TOKEN_LEN = 32  # bytes → 64-char hex string


def _generate_token() -> str:
    return secrets.token_hex(_TOKEN_LEN)


def get_token() -> str:
    """Return the current CSRF token, generating one if absent."""
    if _TOKEN_KEY not in session:
        session[_TOKEN_KEY] = _generate_token()
    return session[_TOKEN_KEY]


def _validate_token() -> bool:
    """Check that the incoming request carries a valid CSRF token."""
    expected = session.get(_TOKEN_KEY)
    if not expected:
        return False
    # Accept token from header (AJAX) or form field (multipart upload)
    provided = (
        request.headers.get("X-CSRF-Token", "")
        or request.form.get(_TOKEN_KEY, "")
    )
    # Constant-time comparison
    return secrets.compare_digest(expected, provided)


def csrf_protect(fn: Callable) -> Callable:
    """
    Decorator: validate CSRF token on POST/PUT/PATCH/DELETE.
    Aborts with 403 on failure.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            if not _validate_token():
                logger.warning(
                    "CSRF validation failed for %s %s from %s",
                    request.method, request.path,
                    request.remote_addr or "unknown",
                )
                abort(403, description="CSRF validation failed.")
        return fn(*args, **kwargs)
    return wrapper


def init_csrf(app: Flask) -> None:
    """
    Register a Jinja2 context processor that makes `csrf_token()`
    available in all templates.
    """
    @app.context_processor
    def inject_csrf():
        return {"csrf_token": get_token}

    logger.info("CSRF protection initialised")

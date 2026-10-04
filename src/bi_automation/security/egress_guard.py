"""
src/bi_automation/security/egress_guard.py

Real (not cosmetic) local-only enforcement.

Monkey-patches socket.socket.connect and socket.create_connection at startup
so any attempt to connect to a non-loopback address raises EgressBlockedError
and logs the blocked host (never the payload).

Set BI_EGRESS_ALLOW_ALL=1 in the environment to disable (dev/CI only).
"""
from __future__ import annotations

import logging
import os
import re
import socket as _socket
from typing import Any

logger = logging.getLogger(__name__)

_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost", ""})
_INSTALLED = False


class EgressBlockedError(ConnectionRefusedError):
    """Raised when an outbound non-loopback connection is attempted."""


def _is_loopback(host: str) -> bool:
    h = (host or "").lower().strip()
    if h in _LOOPBACK_HOSTS:
        return True
    # Resolve numeric loopback patterns
    if h.startswith("127.") or h == "0.0.0.0":
        return True
    return False


def _redact_host(host: str) -> str:
    """Keep only the TLD+1 and first octet — never log full host."""
    h = str(host)
    # IPv4 — keep only first octet
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", h):
        return h.split(".")[0] + ".***"
    # Hostname — keep only TLD
    parts = h.split(".")
    return f"***.{parts[-1]}" if len(parts) > 1 else "***"


# ── Patched connect ────────────────────────────────────────────────────────────
_original_connect = _socket.socket.connect
_original_create_connection = _socket.create_connection


def _patched_connect(self: _socket.socket, address: Any) -> None:  # type: ignore[override]
    host = address[0] if isinstance(address, (tuple, list)) else str(address)
    if not _is_loopback(host):
        logger.warning("EGRESS BLOCKED: outbound connect to %s", _redact_host(host))
        raise EgressBlockedError(
            f"Egress guard: outbound connections are disabled. "
            f"Set BI_EGRESS_ALLOW_ALL=1 to override (dev only)."
        )
    return _original_connect(self, address)


def _patched_create_connection(
    address: tuple[str, int],
    timeout: float = _socket._GLOBAL_DEFAULT_TIMEOUT,  # type: ignore[attr-defined]
    source_address: Any = None,
    **kwargs: Any,
) -> _socket.socket:
    host = address[0] if isinstance(address, (tuple, list)) else str(address)
    if not _is_loopback(host):
        logger.warning("EGRESS BLOCKED: create_connection to %s", _redact_host(host))
        raise EgressBlockedError(
            "Egress guard: outbound connections are disabled."
        )
    return _original_create_connection(address, timeout, source_address, **kwargs)


def install() -> bool:
    """
    Install the egress guard. Idempotent.
    Returns True if installed, False if disabled by env var.
    """
    global _INSTALLED
    if os.environ.get("BI_EGRESS_ALLOW_ALL", "").strip() == "1":
        logger.info("EGRESS GUARD: disabled by BI_EGRESS_ALLOW_ALL=1 (dev mode)")
        return False
    if _INSTALLED:
        return True
    _socket.socket.connect = _patched_connect  # type: ignore[method-assign]
    _socket.create_connection = _patched_create_connection  # type: ignore[assignment]
    _INSTALLED = True
    logger.info("EGRESS GUARD: installed — all non-loopback outbound connections blocked")
    return True


def is_installed() -> bool:
    return _INSTALLED


def audit_report() -> dict[str, Any]:
    """Return a real (not hard-coded) privacy/egress audit dict."""
    # Check for dangerous imports at runtime
    import sys
    dangerous = ["requests", "httpx", "aiohttp", "boto3", "openai", "anthropic"]
    loaded_dangerous = [m for m in dangerous if m in sys.modules]

    return {
        "egress_guard_installed": _INSTALLED,
        "allow_all_override": os.environ.get("BI_EGRESS_ALLOW_ALL", "0") == "1",
        "dangerous_modules_loaded": loaded_dangerous,
        "status": "COMPLIANT" if _INSTALLED and not loaded_dangerous else "NON-COMPLIANT",
    }

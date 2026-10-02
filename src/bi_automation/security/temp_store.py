"""
src/bi_automation/security/temp_store.py

Manages per-session temporary directories under var/tmp/<session_uuid>/.
- Files are saved as var/tmp/<uuid>/input.<ext> (client filename ignored)
- A background reaper thread deletes sessions idle for > TTL seconds
- All cleanup is synchronous on session end / atexit / error
- "Delete my data now" exposed via delete_session(sid)
"""
from __future__ import annotations

import atexit
import logging
import shutil
import threading
import time
import uuid
from pathlib import Path
from typing import Optional

from bi_automation.config.settings import TEMP_DIR
from bi_automation.config.constants import SESSION_TTL_SECONDS, MAX_SESSIONS

logger = logging.getLogger(__name__)

# ── In-memory registry ────────────────────────────────────────────────────────
# { session_id: {"path": Path, "last_access": float, "display_name": str} }
_registry: dict[str, dict] = {}
_lock = threading.Lock()
_reaper_started = False


# ── Public API ────────────────────────────────────────────────────────────────

def create_session(display_name: str = "") -> tuple[str, Path]:
    """
    Allocate a new session: generate UUID, create var/tmp/<uuid>/ directory.
    Returns (session_id, session_dir).
    Enforces MAX_SESSIONS by evicting the oldest idle session.
    """
    with _lock:
        _enforce_max_sessions()
        sid = str(uuid.uuid4())
        session_dir = TEMP_DIR / sid
        session_dir.mkdir(parents=True, exist_ok=True)
        _registry[sid] = {
            "path"         : session_dir,
            "last_access"  : time.monotonic(),
            "display_name" : display_name[:80],  # truncated, never logged raw
        }
    logger.info("Session created: id=%s dir=<uuid>/", sid[:8])
    return sid, session_dir


def touch(sid: str) -> None:
    """Update last-access timestamp for TTL purposes."""
    with _lock:
        if sid in _registry:
            _registry[sid]["last_access"] = time.monotonic()


def get_session_dir(sid: str) -> Optional[Path]:
    with _lock:
        entry = _registry.get(sid)
        if entry:
            entry["last_access"] = time.monotonic()
            return entry["path"]
    return None


def delete_session(sid: str) -> bool:
    """
    Securely delete all files in the session directory and remove from registry.
    Returns True if a session was found and deleted.
    """
    with _lock:
        entry = _registry.pop(sid, None)
    if entry:
        _secure_delete_dir(entry["path"])
        logger.info("Session deleted: id=%s", sid[:8])
        return True
    return False


def session_exists(sid: str) -> bool:
    with _lock:
        return sid in _registry


def save_upload(sid: str, file_bytes: bytes, extension: str) -> Optional[Path]:
    """
    Save uploaded bytes to var/tmp/<uuid>/input.<ext>.
    Client filename is NOT used. Returns the saved path.
    """
    ext = extension.lower().lstrip(".")
    if ext not in {"xlsx", "xls", "xlsm", "csv"}:
        raise ValueError(f"Unsupported extension: {ext}")
    session_dir = get_session_dir(sid)
    if session_dir is None:
        return None
    dest = session_dir / f"input.{ext}"
    dest.write_bytes(file_bytes)
    return dest


# ── Internal helpers ──────────────────────────────────────────────────────────

def _secure_delete_dir(path: Path) -> None:
    """Delete a directory tree. On Windows shutil.rmtree suffices."""
    try:
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
    except Exception as exc:
        logger.warning("Could not fully delete session dir: %s", type(exc).__name__)


def _enforce_max_sessions() -> None:
    """Evict oldest session if over limit. Must be called with _lock held."""
    if len(_registry) >= MAX_SESSIONS:
        oldest_sid = min(_registry, key=lambda s: _registry[s]["last_access"])
        entry = _registry.pop(oldest_sid)
        _secure_delete_dir(entry["path"])
        logger.info("Session evicted (max reached): id=%s", oldest_sid[:8])


def _reap_expired() -> None:
    """Background thread: remove sessions idle > TTL."""
    while True:
        time.sleep(60)  # check every minute
        now = time.monotonic()
        expired = []
        with _lock:
            for sid, entry in list(_registry.items()):
                idle = now - entry["last_access"]
                if idle > SESSION_TTL_SECONDS:
                    expired.append((sid, entry))
            for sid, entry in expired:
                _registry.pop(sid, None)
        for sid, entry in expired:
            _secure_delete_dir(entry["path"])
            logger.info("Session expired (TTL): id=%s", sid[:8])


def _atexit_cleanup() -> None:
    """Clean up all remaining session dirs on app exit."""
    with _lock:
        entries = list(_registry.values())
        _registry.clear()
    for entry in entries:
        _secure_delete_dir(entry["path"])
    logger.info("Atexit cleanup: %d session(s) purged", len(entries))


def start_reaper() -> None:
    """Start the background TTL reaper thread (idempotent)."""
    global _reaper_started
    if _reaper_started:
        return
    t = threading.Thread(target=_reap_expired, daemon=True, name="session-reaper")
    t.start()
    atexit.register(_atexit_cleanup)
    _reaper_started = True
    logger.info("Session reaper started (TTL=%ds)", SESSION_TTL_SECONDS)

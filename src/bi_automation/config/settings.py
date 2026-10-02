"""
src/bi_automation/config/settings.py
Runtime settings — reads SECRET_KEY from file/env, never from source code.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path

# ── Project roots ─────────────────────────────────────────────────────────────
# src/bi_automation/config/settings.py → go up 4 levels to project root
_HERE    = Path(__file__).resolve()
SRC_DIR  = _HERE.parents[2]          # src/
BASE_DIR = _HERE.parents[3]          # project root

VAR_DIR     = BASE_DIR / "var"
TEMP_DIR    = VAR_DIR  / "tmp"
OUTPUT_DIR  = VAR_DIR  / "outputs"
LOG_DIR     = VAR_DIR  / "logs"
LOG_FILE    = LOG_DIR  / "bi_automation.log"

for _d in [TEMP_DIR, OUTPUT_DIR, LOG_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# ── Secret key ────────────────────────────────────────────────────────────────
# Priority:  env var  >  var/.secret_key file  >  generate & save
_SECRET_KEY_FILE = VAR_DIR / ".secret_key"

def _load_or_create_secret_key() -> str:
    """
    Load SECRET_KEY from environment or a local file.
    Generate and persist a new random key on first run.
    Never log or return the key to any external destination.
    """
    env_val = os.environ.get("BI_SECRET_KEY", "").strip()
    if env_val:
        return env_val

    if _SECRET_KEY_FILE.exists():
        return _SECRET_KEY_FILE.read_text().strip()

    # First run — generate, persist (mode 0600)
    import secrets as _secrets
    new_key = _secrets.token_hex(32)
    _SECRET_KEY_FILE.write_text(new_key)
    try:
        os.chmod(_SECRET_KEY_FILE, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass  # Windows doesn't honour chmod the same way — acceptable
    return new_key

SECRET_KEY = _load_or_create_secret_key()

# ── Re-export from constants so callers only need one import ──────────────────
from bi_automation.config.constants import (   # noqa: E402, F401
    FLASK_HOST, FLASK_PORT, MAX_FILE_SIZE_MB,
    ALLOWED_EXTENSIONS, SESSION_TTL_SECONDS,
    LOG_MAX_BYTES, LOG_BACKUP_COUNT, LOG_LEVEL,
)
from bi_automation.config.palette import PALETTE  # noqa: E402, F401

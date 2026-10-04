"""
src/bi_automation/security/log_redaction.py

RedactingFilter: strips sensitive patterns from all log records.
- Quoted strings > 20 chars (likely cell values)
- Email addresses
- Long digit runs (phone numbers, IDs, card numbers)
- File basenames → short hash prefix
- Column values that slipped through as log arguments

Attach to the root logger after basicConfig / RotatingFileHandler.
"""
from __future__ import annotations

import hashlib
import logging
import re
from typing import Any

# ── Patterns to redact ────────────────────────────────────────────────────────
_QUOTED_LONG   = re.compile(r"""(['"])[^'"]{21,}(['"])""")
_EMAIL         = re.compile(r"[\w.+-]{2,}@[\w.-]{3,}\.[a-z]{2,}", re.I)
_LONG_DIGITS   = re.compile(r"\b\d{8,}\b")
_XLSX_PATH     = re.compile(r"[^\s/\\]+\.(?:xlsx|xls|xlsm|csv)", re.I)


def _hash6(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:6]


def _redact(msg: str) -> str:
    msg = _QUOTED_LONG.sub(lambda m: f"{m.group(1)}<redacted>{m.group(2)}", msg)
    msg = _EMAIL.sub("<email>", msg)
    msg = _LONG_DIGITS.sub("<digits>", msg)
    msg = _XLSX_PATH.sub(lambda m: f"file-{_hash6(m.group())}.xlsx", msg)
    return msg


class RedactingFilter(logging.Filter):
    """
    Logging filter that scrubs potentially sensitive data from log records
    before they are written to disk or console.
    """

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        try:
            # Redact the formatted message
            record.msg = _redact(str(record.msg))
            # Redact any string args too
            if record.args:
                if isinstance(record.args, dict):
                    record.args = {
                        k: _redact(str(v)) if isinstance(v, str) else v
                        for k, v in record.args.items()
                    }
                elif isinstance(record.args, tuple):
                    record.args = tuple(
                        _redact(str(a)) if isinstance(a, str) else a
                        for a in record.args
                    )
        except Exception:
            pass  # Never let the filter itself cause a logging failure
        return True  # Always pass — we only redact, never drop


def install_on_root() -> None:
    """Attach RedactingFilter to every handler on the root logger."""
    f = RedactingFilter()
    root = logging.getLogger()
    for handler in root.handlers:
        if not any(isinstance(h, RedactingFilter) for h in handler.filters):
            handler.addFilter(f)
    logger = logging.getLogger(__name__)
    logger.debug("RedactingFilter installed on %d handlers", len(root.handlers))

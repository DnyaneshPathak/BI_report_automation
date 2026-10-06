"""
security/file_security.py
--------------------------
Handles safe file validation for Excel uploads.

Responsibilities:
  - Extension whitelist enforcement
  - File-size limit enforcement
  - Excel structural validation
  - Safe filename sanitisation
  - Formula-injection detection
"""

from __future__ import annotations

import logging
import os
import re
import unicodedata
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS  = {".xlsx", ".xls", ".xlsm", ".csv"}
MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024   # 200 MB

# Patterns that might indicate formula injection in cell values
_FORMULA_INJECTION_PATTERNS = re.compile(
    r"^[\+\-\=\@]",   # starts with =, +, -, @
)


def validate_file(file_path: Path) -> Tuple[bool, str]:
    """
    Validate an Excel file path.

    Returns
    -------
    (True, "") on success
    (False, reason) on failure
    """
    # Extension check
    ext = file_path.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}."

    # Existence check
    if not file_path.exists():
        return False, "File does not exist."

    # Size check
    size = file_path.stat().st_size
    if size == 0:
        return False, "The file is empty (0 bytes)."
    if size > MAX_FILE_SIZE_BYTES:
        mb = size / (1024 * 1024)
        return False, f"File is too large ({mb:.1f} MB). Maximum allowed is 200 MB."

    # Quick structural check — try opening with openpyxl
    if ext in {".xlsx", ".xlsm"}:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(str(file_path), read_only=True, data_only=True)
            wb.close()
        except Exception as exc:
            msg = str(exc)
            if "encrypted" in msg.lower() or "password" in msg.lower():
                return False, "The workbook is password-protected. Please remove the password before uploading."
            return False, f"Cannot open workbook: {msg}"

    logger.info("FILE SECURITY: File passed validation — %s (%d KB)", file_path.name, size // 1024)
    return True, ""


def sanitize_filename(name: str) -> str:
    """
    Return a filesystem-safe filename stem (without extension).
    Strips special characters; replaces spaces with underscores.
    """
    # Normalize unicode
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    # Keep only alphanumeric, dash, underscore, dot
    name = re.sub(r"[^\w\s\-]", "", name)
    name = re.sub(r"\s+", "_", name).strip("_")
    if not name:
        name = "workbook"
    return name[:100]   # cap length


def check_formula_injection(value: str) -> bool:
    """Return True if value looks like a formula-injection attempt."""
    if isinstance(value, str):
        return bool(_FORMULA_INJECTION_PATTERNS.match(value.strip()))
    return False

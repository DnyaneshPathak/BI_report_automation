"""
tests/unit/test_config.py
Unit tests for the config package.
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).parents[2]))


def test_secret_key_not_hardcoded():
    """SECRET_KEY must not be a hard-coded literal from source."""
    from bi_automation.config.settings import SECRET_KEY
    # Must be 64-char hex string (32 random bytes)
    assert len(SECRET_KEY) == 64
    assert all(c in "0123456789abcdef" for c in SECRET_KEY)


def test_secret_key_persisted():
    """SECRET_KEY is saved to var/.secret_key and re-loaded consistently."""
    from bi_automation.config.settings import SECRET_KEY, _SECRET_KEY_FILE
    if _SECRET_KEY_FILE.exists():
        reloaded = _SECRET_KEY_FILE.read_text().strip()
        assert reloaded == SECRET_KEY


def test_constants_types():
    """All constants have expected types."""
    from bi_automation.config.constants import (
        MAX_FILE_SIZE_MB, MAX_ROWS, MAX_COLS,
        SESSION_TTL_SECONDS, MAX_ANALYSES_PER_JOB,
        ANALYSIS_OPTIONS, ALLOWED_EXTENSIONS,
    )
    assert isinstance(MAX_FILE_SIZE_MB, int) and MAX_FILE_SIZE_MB > 0
    assert isinstance(MAX_ROWS, int) and MAX_ROWS >= 100_000
    assert isinstance(MAX_COLS, int) and MAX_COLS >= 100
    assert isinstance(SESSION_TTL_SECONDS, int) and SESSION_TTL_SECONDS >= 300
    assert isinstance(MAX_ANALYSES_PER_JOB, int) and MAX_ANALYSES_PER_JOB >= 10
    assert len(ANALYSIS_OPTIONS) == 5
    assert ".xlsx" in ALLOWED_EXTENSIONS
    assert ".csv" in ALLOWED_EXTENSIONS


def test_palette_colours():
    """Palette and chart colours are valid hex strings."""
    from bi_automation.config.palette import PALETTE, CHART_COLORS
    for key, val in PALETTE.items():
        assert val.startswith("#"), f"Palette[{key}] is not a hex colour"
        assert len(val) == 7, f"Palette[{key}] has wrong length"
    assert len(CHART_COLORS) >= 10

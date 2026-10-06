"""
tests/security/test_no_secrets_in_source.py

Pre-commit style checks:
  - No SECRET_KEY literal in source files
  - No hardcoded http/https URLs pointing outside localhost
  - No data files committed (xlsx/xls/xlsm/csv) in src/ or tests/
  - No dangerous import (requests, openai, anthropic, boto3, etc.)
"""
import re
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).parents[2]
_SRC  = _ROOT / "src"
_TESTS = _ROOT / "tests"

DANGEROUS_IMPORTS = [
    "requests",  "httpx", "aiohttp",
    "boto3", "openai", "anthropic", "google.generativeai",
    "azure", "gcloud",
]

EXTERNAL_URL_PATTERN = re.compile(
    r'https?://(?!(?:127\.0\.0\.1|localhost))',
    re.IGNORECASE,
)

HARDCODED_KEY_PATTERN = re.compile(
    r'SECRET_KEY\s*=\s*["\'][^"\']{10,}["\']',
)


def _all_py_files():
    return list(_SRC.rglob("*.py")) + list(_TESTS.rglob("*.py")) + [_ROOT / "main.py"]


def _all_template_files():
    tmpl = _SRC / "bi_automation" / "web" / "templates"
    return list(tmpl.rglob("*.html")) if tmpl.exists() else []


@pytest.mark.parametrize("py_file", _all_py_files())
def test_no_hardcoded_secret_key(py_file):
    """No SECRET_KEY = '...' literal in any Python source file."""
    content = py_file.read_text(encoding="utf-8", errors="replace")
    matches = HARDCODED_KEY_PATTERN.findall(content)
    assert not matches, f"{py_file.name}: hardcoded SECRET_KEY found: {matches}"


@pytest.mark.parametrize("py_file", _all_py_files())
def test_no_dangerous_imports(py_file):
    """No external network/cloud library imports in source."""
    content = py_file.read_text(encoding="utf-8", errors="replace")
    for lib in DANGEROUS_IMPORTS:
        pattern = re.compile(rf"^\s*(?:import|from)\s+{re.escape(lib)}\b", re.MULTILINE)
        if pattern.search(content):
            pytest.fail(f"{py_file.name}: dangerous import '{lib}' found")


@pytest.mark.parametrize("py_file", _all_py_files())
def test_no_external_urls_in_source(py_file):
    """No external http/https URLs (except in comments and docstrings)."""
    lines = py_file.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Allow comments and doc-style lines
        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        if EXTERNAL_URL_PATTERN.search(stripped):
            # Ignore format-string placeholders like http://%s:%s (log lines)
            cleaned = re.sub(r"https?://%s[^'\"]*", "", stripped)
            if EXTERNAL_URL_PATTERN.search(cleaned):
                pytest.fail(f"{py_file.name}:{i}: external URL found: {stripped[:120]}")


def test_no_data_files_in_src():
    """No Excel/CSV data files in src/ or tests/."""
    data_extensions = {".xlsx", ".xls", ".xlsm", ".csv"}
    found = []
    for ext in data_extensions:
        found.extend(_SRC.rglob(f"*{ext}"))
        found.extend(_TESTS.rglob(f"*{ext}"))
    assert not found, f"Data files found in src/ or tests/: {[f.name for f in found]}"


def test_no_external_urls_in_templates():
    """No external http/https URLs in HTML templates."""
    for tmpl in _all_template_files():
        content = tmpl.read_text(encoding="utf-8", errors="replace")
        matches = EXTERNAL_URL_PATTERN.findall(content)
        assert not matches, f"{tmpl.name}: external URLs found: {matches}"

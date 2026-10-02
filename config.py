"""
Central configuration for BI Report Automation.
All values are local-only — no cloud, no external API.
"""

import os
from pathlib import Path

# ── Project Root ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()

# ── Directories ──────────────────────────────────────────────────────────────
TEMP_DIR    = BASE_DIR / "temp"
OUTPUT_DIR  = BASE_DIR / "outputs"
STATIC_DIR  = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "templates"

for _d in [TEMP_DIR, OUTPUT_DIR]:
    _d.mkdir(exist_ok=True)

# ── Upload limits ─────────────────────────────────────────────────────────────
MAX_FILE_SIZE_MB = 200
ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".xlsm"}

# ── Profiling thresholds ──────────────────────────────────────────────────────
HIGH_CARDINALITY_THRESHOLD   = 50     # unique% above which cat is "high-card"
LOW_CARDINALITY_MAX          = 30     # max unique values for a donut/pie
ID_MAX_UNIQUE_RATIO          = 0.95   # if unique% > 95 → likely an ID
RARE_CATEGORY_THRESHOLD      = 0.01   # categories < 1% frequency are "rare"
OUTLIER_IQR_MULTIPLIER       = 1.5
OUTLIER_ZSCORE_THRESHOLD     = 3.0
MIN_ROWS_FOR_STAT_TEST       = 30
CORRELATION_STRONG_THRESHOLD = 0.6
CORRELATION_MODERATE_THRESHOLD = 0.3

# ── Dashboard ─────────────────────────────────────────────────────────────────
MAX_KPI_CARDS       = 6
MAX_VISUALS_PER_PAGE = 7
MAX_SLICERS_PER_PAGE = 5

# ── Color palette (corporate) ─────────────────────────────────────────────────
PALETTE = {
    "primary"     : "#1B2A4A",   # dark navy
    "secondary"   : "#2563EB",   # blue
    "accent"      : "#3B82F6",
    "background"  : "#F8FAFC",
    "surface"     : "#FFFFFF",
    "border"      : "#E2E8F0",
    "text_primary": "#0F172A",
    "text_secondary": "#64748B",
    "success"     : "#059669",
    "warning"     : "#D97706",
    "danger"      : "#DC2626",
    "chart_colors": [
        "#2563EB", "#059669", "#D97706", "#7C3AED",
        "#DB2777", "#0891B2", "#EA580C", "#65A30D",
    ],
}

# ── Flask ─────────────────────────────────────────────────────────────────────
FLASK_HOST   = "127.0.0.1"
FLASK_PORT   = 5050
FLASK_DEBUG  = False
SECRET_KEY   = "bi-report-automation-local-secret-k3y-2024-do-not-share"

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE = BASE_DIR / "bi_automation.log"
LOG_LEVEL = "INFO"   # never log raw data rows

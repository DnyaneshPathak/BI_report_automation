"""
src/bi_automation/config/constants.py
All magic numbers and config constants in one place.
"""

# ── Analysis options ──────────────────────────────────────────────────────────
ANALYSIS_OPTIONS = [
    "univariate",
    "bivariate",
    "multivariate",
    "statistical",
    "probability",
]

# ── Upload limits ─────────────────────────────────────────────────────────────
MAX_FILE_SIZE_MB        = 200
MAX_ROWS                = 1_000_000
MAX_COLS                = 500
MAX_CONCURRENT_JOBS     = 2
ALLOWED_EXTENSIONS      = {".xlsx", ".xls", ".xlsm", ".csv"}

# ── Session / TTL ─────────────────────────────────────────────────────────────
SESSION_TTL_SECONDS     = 1800   # 30 min idle
MAX_SESSIONS            = 20

# ── Analysis limits ───────────────────────────────────────────────────────────
MAX_ANALYSES_PER_JOB    = 60
MAX_DESCRIPTION_CHARS   = 500
MAX_BIVARIATE_PARTNERS  = 1
MAX_MULTIVARIATE_PARTNERS = 4

# ── Profiling thresholds ──────────────────────────────────────────────────────
HIGH_CARDINALITY_THRESHOLD    = 50     # unique % above which cat is "high-card"
LOW_CARDINALITY_MAX           = 30     # max unique values for a donut/pie
ID_MAX_UNIQUE_RATIO           = 0.95   # unique% > 95 → likely an ID
RARE_CATEGORY_THRESHOLD       = 0.01   # < 1% frequency → "rare"
OUTLIER_IQR_MULTIPLIER        = 1.5
OUTLIER_ZSCORE_THRESHOLD      = 3.0
MIN_ROWS_FOR_STAT_TEST        = 30
CORRELATION_STRONG_THRESHOLD  = 0.6
CORRELATION_MODERATE_THRESHOLD = 0.3

# ── Driver analysis / goal mode ───────────────────────────────────────────────
TRIVIAL_CRAMER_V              = 0.10
TRIVIAL_COHENS_D              = 0.20
TRIVIAL_RATE_DIFF_PCT         = 2.0    # percentage points
MIN_SEGMENT_ROWS              = 30
MAX_DRIVER_FEATURES           = 20

# ── Dashboard layout ──────────────────────────────────────────────────────────
MAX_KPI_CARDS           = 6
MAX_CHARTS_PER_PAGE     = 8
MAX_SLICERS_PER_PAGE    = 5
MAX_PIE_SLICES          = 8
MAX_CHART_POINTS        = 5_000     # downsample beyond this (LTTB / binning)

# ── Server ───────────────────────────────────────────────────────────────────
FLASK_HOST  = "127.0.0.1"
FLASK_PORT  = 5050

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_MAX_BYTES   = 1_048_576    # 1 MB per file
LOG_BACKUP_COUNT = 5
LOG_LEVEL       = "INFO"

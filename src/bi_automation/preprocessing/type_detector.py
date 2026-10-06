"""
preprocessing/datatype_detector.py
------------------------------------
Detects analytical types for every column and assigns a feature role.

Analytical Types
  continuous | discrete_numeric | categorical_nominal |
  categorical_ordinal | binary | datetime | identifier | text

Feature Roles
  Identifier | Measure | Dimension | Time Dimension | Category |
  Location | Status | Target-Like Metric | Financial Measure |
  Quantity | Percentage | Duration | Ranking Variable | Descriptive Text
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)

# ── Keyword patterns for heuristic role assignment ────────────────────────────
_ID_PATTERNS     = re.compile(r"\b(id|code|no|num|number|ref|key|uuid|serial)\b", re.I)
_DATE_PATTERNS   = re.compile(r"\b(date|time|year|month|day|quarter|week|period|created|updated|booked|travel|birth|hire)\b", re.I)
_GEO_PATTERNS    = re.compile(r"\b(country|city|state|region|province|district|zip|postal|latitude|longitude|lat|lon|location|geo)\b", re.I)
_FINANCIAL_PATTERNS = re.compile(r"\b(revenue|sales|profit|cost|price|amount|value|fee|charge|spend|budget|income|loss|margin|earning|payment|invoice)\b", re.I)
_QUANTITY_PATTERNS  = re.compile(r"\b(quantity|qty|count|volume|units?|transactions?|orders?|bookings?|tickets?|seats?|passengers?)\b", re.I)
_PERCENT_PATTERNS   = re.compile(r"\b(rate|ratio|percentage|pct|%|share|proportion|conversion|churn|cancell)\b", re.I)
_DURATION_PATTERNS  = re.compile(r"\b(duration|length|hours?|minutes?|seconds?|days?|nights?|stay|elapsed)\b", re.I)
_STATUS_PATTERNS    = re.compile(r"\b(status|state|flag|indicator|active|type|category|class|segment|tier|level|grade)\b", re.I)

ORDINAL_KEYWORDS = {
    frozenset({"low", "medium", "high"}),
    frozenset({"low", "medium", "high", "very high"}),
    frozenset({"poor", "average", "good", "excellent"}),
    frozenset({"bad", "neutral", "good"}),
    frozenset({"1", "2", "3", "4", "5"}),
    frozenset({"bronze", "silver", "gold", "platinum"}),
    frozenset({"small", "medium", "large"}),
    frozenset({"junior", "mid", "senior"}),
    frozenset({"beginner", "intermediate", "advanced"}),
}


@dataclass
class ColumnProfile:
    name: str
    analytical_type: str = "unknown"
    feature_role: str = "unknown"
    include_in_analysis: bool = True
    reason: str = ""


class DataTypeDetector:
    """
    Detects the analytical type and business role of each DataFrame column.
    Returns a dict mapping column_name → ColumnProfile.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.n_rows = len(df)

    def detect_all(self) -> Dict[str, ColumnProfile]:
        profiles: Dict[str, ColumnProfile] = {}
        for col in self.df.columns:
            profiles[col] = self._classify_column(col)
        return profiles

    # ── Main classification logic ─────────────────────────────────────────────
    def _classify_column(self, col: str) -> ColumnProfile:
        series = self.df[col]
        profile = ColumnProfile(name=col)

        n_unique   = series.nunique(dropna=True)
        n_notna    = series.notna().sum()
        unique_ratio = n_unique / max(n_notna, 1)

        # --- Step 1: Try coerce to datetime ---
        if self._is_datetime(series, col):
            profile.analytical_type = "datetime"
            profile.feature_role    = "Time Dimension"
            return profile

        # --- Step 2: Try coerce to numeric ---
        numeric_series = self._to_numeric(series)
        is_numeric = numeric_series is not None

        if is_numeric:
            # --- Step 2a: Identifier heuristic ---
            if unique_ratio > 0.95 or _ID_PATTERNS.search(col):
                if self._looks_like_id(series, numeric_series):
                    profile.analytical_type    = "identifier"
                    profile.feature_role       = "Identifier"
                    profile.include_in_analysis = False
                    profile.reason             = "High unique ratio / ID-like name."
                    return profile

            # --- Step 2b: Binary ---
            uniq_vals = set(numeric_series.dropna().unique())
            if uniq_vals <= {0, 1} or (n_unique == 2 and self._is_binary(series)):
                profile.analytical_type = "binary"
                profile.feature_role    = "Status"
                return profile

            # --- Step 2c: Discrete vs Continuous ---
            if _PERCENT_PATTERNS.search(col):
                profile.analytical_type = "continuous"
                profile.feature_role    = "Percentage"
                return profile
            if _DURATION_PATTERNS.search(col):
                profile.analytical_type = "continuous"
                profile.feature_role    = "Duration"
                return profile
            if _FINANCIAL_PATTERNS.search(col):
                profile.analytical_type = "continuous"
                profile.feature_role    = "Financial Measure"
                return profile
            if _QUANTITY_PATTERNS.search(col):
                profile.analytical_type = "discrete_numeric"
                profile.feature_role    = "Quantity"
                return profile

            # General numeric: discrete if all integers and low unique, else continuous
            all_int = (numeric_series.dropna() % 1 == 0).all()
            if all_int and n_unique <= 30:
                profile.analytical_type = "discrete_numeric"
                profile.feature_role    = "Quantity"
            else:
                profile.analytical_type = "continuous"
                profile.feature_role    = "Measure"
            return profile

        # --- Step 3: Categorical ---
        str_series = series.dropna().astype(str).str.strip().str.lower()

        # Binary string?
        uniq_str = set(str_series.unique())
        if len(uniq_str) == 2 and uniq_str <= {"yes", "no"} | {"true", "false"} | {"0", "1"} | {"y", "n"} | {"active", "inactive"}:
            profile.analytical_type = "binary"
            profile.feature_role    = "Status"
            return profile

        # ID by column name + high cardinality
        if _ID_PATTERNS.search(col) and unique_ratio > 0.5:
            profile.analytical_type    = "identifier"
            profile.feature_role       = "Identifier"
            profile.include_in_analysis = False
            return profile

        # Ordinal?
        if any(frozenset(uniq_str) <= ordinal_set or frozenset(uniq_str) >= ordinal_set for ordinal_set in ORDINAL_KEYWORDS):
            profile.analytical_type = "categorical_ordinal"
            profile.feature_role    = "Category"
            return profile

        # High-cardinality string → descriptive text
        if unique_ratio > 0.6 and n_unique > 50:
            profile.analytical_type    = "text"
            profile.feature_role       = "Descriptive Text"
            profile.include_in_analysis = False
            return profile

        # Geo?
        if _GEO_PATTERNS.search(col):
            profile.analytical_type = "categorical_nominal"
            profile.feature_role    = "Location"
            return profile

        # Status?
        if _STATUS_PATTERNS.search(col):
            profile.analytical_type = "categorical_nominal"
            profile.feature_role    = "Status"
            return profile

        # Default: categorical nominal
        profile.analytical_type = "categorical_nominal"
        profile.feature_role    = "Dimension"
        return profile

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _is_datetime(self, series: pd.Series, col_name: str) -> bool:
        """Return True if column can be parsed as dates."""
        if pd.api.types.is_datetime64_any_dtype(series):
            return True
        if not _DATE_PATTERNS.search(col_name):
            return False
        sample = series.dropna().astype(str).head(20)
        try:
            parsed = pd.to_datetime(sample, infer_datetime_format=True, errors="coerce")
            success_rate = parsed.notna().mean()
            return success_rate > 0.7
        except Exception:
            return False

    def _to_numeric(self, series: pd.Series) -> Optional[pd.Series]:
        """Try to coerce series to numeric; return None on failure."""
        if pd.api.types.is_numeric_dtype(series):
            return series
        cleaned = (
            series.astype(str)
            .str.replace(r"[₹$€£¥,\s%]", "", regex=True)
            .str.strip()
        )
        numeric = pd.to_numeric(cleaned, errors="coerce")
        success_rate = numeric.notna().sum() / max(series.notna().sum(), 1)
        if success_rate > 0.7:
            return numeric
        return None

    def _looks_like_id(self, series: pd.Series, numeric: pd.Series) -> bool:
        """Heuristic: integer with very high unique ratio."""
        all_int = (numeric.dropna() % 1 == 0).all()
        unique_ratio = series.nunique() / max(len(series.dropna()), 1)
        return all_int and unique_ratio > 0.95

    def _is_binary(self, series: pd.Series) -> bool:
        vals = {str(v).strip().lower() for v in series.dropna().unique()}
        binary_sets = [
            {"yes", "no"}, {"true", "false"}, {"0", "1"},
            {"y", "n"}, {"active", "inactive"}, {"pass", "fail"},
        ]
        return any(vals == s for s in binary_sets)

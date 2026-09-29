"""
analysis/profiler.py
---------------------
Computes a comprehensive internal data profile for every column.

Per-column metrics include:
  count, unique count/%, missing count/%, min, max, mean, median, mode,
  std, variance, range, Q1, Q3, IQR, skewness, kurtosis, CV,
  zero count, negative count, outlier count, cardinality,
  frequency distribution (categorical), date range (datetime).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats

from preprocessing.datatype_detector import ColumnProfile
from preprocessing.outliers import OutlierAnalyser

logger = logging.getLogger(__name__)


@dataclass
class ColumnStats:
    name: str
    analytical_type: str
    feature_role: str
    count: int = 0
    unique_count: int = 0
    unique_pct: float = 0.0
    missing_count: int = 0
    missing_pct: float = 0.0
    # numeric
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    mean: Optional[float] = None
    median: Optional[float] = None
    mode: Any = None
    std: Optional[float] = None
    variance: Optional[float] = None
    data_range: Optional[float] = None
    q1: Optional[float] = None
    q3: Optional[float] = None
    iqr: Optional[float] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    cv: Optional[float] = None
    zero_count: int = 0
    negative_count: int = 0
    outlier_count: int = 0
    # categorical
    top_category: Optional[str] = None
    least_category: Optional[str] = None
    freq_distribution: Dict[str, float] = field(default_factory=dict)
    rare_categories: List[str] = field(default_factory=list)
    # datetime
    earliest_date: Optional[str] = None
    latest_date: Optional[str] = None
    date_range_days: Optional[int] = None


class DataProfiler:

    def __init__(self, df: pd.DataFrame, profiles: Dict[str, ColumnProfile]):
        self.df       = df
        self.profiles = profiles
        self.n_rows   = len(df)

    def profile_all(self) -> Dict[str, ColumnStats]:
        # Run outlier analysis first
        outlier_results = OutlierAnalyser(self.df, self.profiles).analyse()

        column_stats: Dict[str, ColumnStats] = {}
        for col, profile in self.profiles.items():
            if col not in self.df.columns:
                continue
            cs = ColumnStats(
                name            = col,
                analytical_type = profile.analytical_type,
                feature_role    = profile.feature_role,
            )
            series = self.df[col]
            cs.count         = int(series.notna().sum())
            cs.unique_count  = int(series.nunique(dropna=True))
            cs.unique_pct    = round(cs.unique_count / max(self.n_rows, 1) * 100, 2)
            cs.missing_count = int(series.isna().sum())
            cs.missing_pct   = round(cs.missing_count / max(self.n_rows, 1) * 100, 2)

            if profile.analytical_type in ("continuous", "discrete_numeric"):
                self._profile_numeric(series, cs, outlier_results.get(col))
            elif profile.analytical_type in ("categorical_nominal", "categorical_ordinal", "binary"):
                self._profile_categorical(series, cs)
            elif profile.analytical_type == "datetime":
                self._profile_datetime(series, cs)

            column_stats[col] = cs
        return column_stats

    # ── Numeric profiling ─────────────────────────────────────────────────────
    def _profile_numeric(self, series: pd.Series, cs: ColumnStats, outlier_result=None) -> None:
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if len(numeric) == 0:
            return
        cs.minimum  = round(float(numeric.min()), 4)
        cs.maximum  = round(float(numeric.max()), 4)
        cs.mean     = round(float(numeric.mean()), 4)
        cs.median   = round(float(numeric.median()), 4)
        mode_result = numeric.mode()
        cs.mode     = round(float(mode_result.iloc[0]), 4) if len(mode_result) > 0 else None
        cs.std      = round(float(numeric.std()), 4) if len(numeric) > 1 else 0.0
        cs.variance = round(float(numeric.var()), 4) if len(numeric) > 1 else 0.0
        cs.data_range = round(cs.maximum - cs.minimum, 4)
        cs.q1       = round(float(numeric.quantile(0.25)), 4)
        cs.q3       = round(float(numeric.quantile(0.75)), 4)
        cs.iqr      = round(cs.q3 - cs.q1, 4)
        cs.skewness = round(float(stats.skew(numeric)), 4) if len(numeric) > 2 else None
        cs.kurtosis = round(float(stats.kurtosis(numeric)), 4) if len(numeric) > 3 else None
        cs.cv       = round(cs.std / abs(cs.mean) * 100, 2) if cs.mean and cs.mean != 0 else None
        cs.zero_count     = int((numeric == 0).sum())
        cs.negative_count = int((numeric < 0).sum())
        cs.outlier_count  = outlier_result.total_detected if outlier_result else 0

    # ── Categorical profiling ─────────────────────────────────────────────────
    def _profile_categorical(self, series: pd.Series, cs: ColumnStats) -> None:
        valid = series.dropna().astype(str)
        if len(valid) == 0:
            return
        freq = valid.value_counts()
        pct  = (freq / len(valid) * 100).round(2)
        cs.freq_distribution = dict(pct.head(20))   # top 20 categories
        if len(freq) > 0:
            cs.top_category   = str(freq.index[0])
            cs.least_category = str(freq.index[-1])
        cs.rare_categories = list(pct[pct < 1.0].index[:10])
        # Mode
        cs.mode = cs.top_category

    # ── Datetime profiling ────────────────────────────────────────────────────
    def _profile_datetime(self, series: pd.Series, cs: ColumnStats) -> None:
        dt = pd.to_datetime(series, errors="coerce").dropna()
        if len(dt) == 0:
            return
        cs.earliest_date   = str(dt.min().date())
        cs.latest_date     = str(dt.max().date())
        cs.date_range_days = (dt.max() - dt.min()).days

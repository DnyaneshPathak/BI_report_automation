"""
analysis/univariate.py
-----------------------
Performs univariate analysis for each eligible column.

Continuous: distribution summary, percentiles, histogram data.
Categorical: frequency + percentage distributions.
Datetime: trend data by year / quarter / month.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats

from preprocessing.datatype_detector import ColumnProfile
from analysis.profiler import ColumnStats

logger = logging.getLogger(__name__)


@dataclass
class UnivariateResult:
    column: str
    analytical_type: str
    # Numeric
    histogram_bins: List[float] = field(default_factory=list)
    histogram_counts: List[int] = field(default_factory=list)
    percentiles: Dict[str, float] = field(default_factory=dict)
    distribution_shape: str = ""          # normal | right-skewed | left-skewed | bimodal | uniform
    # Categorical
    category_labels: List[str] = field(default_factory=list)
    category_counts: List[int] = field(default_factory=list)
    category_pct: List[float] = field(default_factory=list)
    # Datetime
    trend_by_year: Dict[str, int] = field(default_factory=dict)
    trend_by_month: Dict[str, int] = field(default_factory=dict)
    trend_by_quarter: Dict[str, int] = field(default_factory=dict)


class UnivariateAnalyser:

    def __init__(self, df: pd.DataFrame, profiles: Dict[str, ColumnProfile], col_stats: Dict[str, ColumnStats]):
        self.df        = df
        self.profiles  = profiles
        self.col_stats = col_stats

    def analyse(self) -> Dict[str, UnivariateResult]:
        results: Dict[str, UnivariateResult] = {}
        for col, profile in self.profiles.items():
            if col not in self.df.columns or not profile.include_in_analysis:
                continue
            atype = profile.analytical_type
            result = UnivariateResult(column=col, analytical_type=atype)

            if atype in ("continuous", "discrete_numeric"):
                self._analyse_numeric(col, result)
            elif atype in ("categorical_nominal", "categorical_ordinal", "binary"):
                self._analyse_categorical(col, result)
            elif atype == "datetime":
                self._analyse_datetime(col, result)
            else:
                continue

            results[col] = result
        return results

    # ── Numeric ───────────────────────────────────────────────────────────────
    def _analyse_numeric(self, col: str, result: UnivariateResult) -> None:
        numeric = pd.to_numeric(self.df[col], errors="coerce").dropna()
        if len(numeric) < 5:
            return

        # Histogram (up to 20 bins)
        n_bins = min(20, int(np.sqrt(len(numeric))))
        counts, bin_edges = np.histogram(numeric, bins=n_bins)
        result.histogram_bins   = [round(float(e), 4) for e in bin_edges]
        result.histogram_counts = [int(c) for c in counts]

        # Percentiles
        result.percentiles = {
            "p5" : round(float(np.percentile(numeric, 5)), 4),
            "p25": round(float(np.percentile(numeric, 25)), 4),
            "p50": round(float(np.percentile(numeric, 50)), 4),
            "p75": round(float(np.percentile(numeric, 75)), 4),
            "p90": round(float(np.percentile(numeric, 90)), 4),
            "p95": round(float(np.percentile(numeric, 95)), 4),
            "p99": round(float(np.percentile(numeric, 99)), 4),
        }

        # Distribution shape heuristic
        skew = float(stats.skew(numeric))
        kurt = float(stats.kurtosis(numeric))
        if abs(skew) < 0.5:
            result.distribution_shape = "approximately normal"
        elif skew > 1.0:
            result.distribution_shape = "right-skewed (positively skewed)"
        elif skew < -1.0:
            result.distribution_shape = "left-skewed (negatively skewed)"
        else:
            result.distribution_shape = "moderately skewed"

    # ── Categorical ───────────────────────────────────────────────────────────
    def _analyse_categorical(self, col: str, result: UnivariateResult) -> None:
        valid = self.df[col].dropna().astype(str)
        if len(valid) == 0:
            return
        freq = valid.value_counts()
        pct  = (freq / len(valid) * 100).round(2)
        # Show top 30 categories maximum
        top_freq = freq.head(30)
        top_pct  = pct.head(30)
        result.category_labels = list(top_freq.index)
        result.category_counts = [int(v) for v in top_freq.values]
        result.category_pct    = [float(v) for v in top_pct.values]

    # ── Datetime ──────────────────────────────────────────────────────────────
    def _analyse_datetime(self, col: str, result: UnivariateResult) -> None:
        dt = pd.to_datetime(self.df[col], errors="coerce").dropna()
        if len(dt) < 2:
            return

        # Yearly trend (count of records per year)
        year_counts = dt.dt.year.value_counts().sort_index()
        result.trend_by_year = {str(k): int(v) for k, v in year_counts.items()}

        # Monthly trend
        month_counts = dt.dt.to_period("M").value_counts().sort_index()
        result.trend_by_month = {str(k): int(v) for k, v in month_counts.items()}

        # Quarterly trend
        quarter_counts = dt.dt.to_period("Q").value_counts().sort_index()
        result.trend_by_quarter = {str(k): int(v) for k, v in quarter_counts.items()}

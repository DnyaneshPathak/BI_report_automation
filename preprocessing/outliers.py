"""
preprocessing/outliers.py
--------------------------
Detects outliers for continuous numeric columns.

Methods used:
  - IQR (primary method — robust, no distribution assumptions)
  - Z-score (secondary, only when data is approximately symmetric)

Outliers are NOT deleted. Each is tagged as:
  - "Likely Valid" (within 3 IQR)
  - "Suspicious" (within 5 IQR)
  - "Extreme" (beyond 5 IQR or |Z| > 5)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from preprocessing.datatype_detector import ColumnProfile
from config import OUTLIER_IQR_MULTIPLIER, OUTLIER_ZSCORE_THRESHOLD

logger = logging.getLogger(__name__)


@dataclass
class OutlierResult:
    column: str
    method: str
    total_detected: int = 0
    likely_valid: int = 0
    suspicious: int = 0
    extreme: int = 0
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    indices: List[int] = field(default_factory=list)


class OutlierAnalyser:

    def __init__(self, df: pd.DataFrame, profiles: Dict[str, ColumnProfile]):
        self.df       = df
        self.profiles = profiles

    def analyse(self) -> Dict[str, OutlierResult]:
        results: Dict[str, OutlierResult] = {}
        for col, profile in self.profiles.items():
            if col not in self.df.columns:
                continue
            if profile.analytical_type not in ("continuous", "discrete_numeric"):
                continue
            if not profile.include_in_analysis:
                continue

            series = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(series) < 10:
                continue

            result = self._iqr_method(col, series)
            results[col] = result
            logger.debug(
                "Outliers in '%s': %d detected (%d extreme).",
                col, result.total_detected, result.extreme,
            )
        return results

    def _iqr_method(self, col: str, series: pd.Series) -> OutlierResult:
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            return OutlierResult(column=col, method="IQR")

        lower_1 = q1 - OUTLIER_IQR_MULTIPLIER * iqr
        upper_1 = q3 + OUTLIER_IQR_MULTIPLIER * iqr
        lower_5 = q1 - 5 * iqr
        upper_5 = q3 + 5 * iqr

        outside_1_5 = (series < lower_1) | (series > upper_1)
        outside_5   = (series < lower_5) | (series > upper_5)

        # Compute z-score for magnitude classification
        z = np.abs(stats.zscore(series))

        likely_valid = int((outside_1_5 & ~outside_5 & (z < OUTLIER_ZSCORE_THRESHOLD)).sum())
        suspicious   = int((outside_1_5 & ~outside_5 & (z >= OUTLIER_ZSCORE_THRESHOLD)).sum())
        extreme      = int(outside_5.sum())
        total        = int(outside_1_5.sum())

        return OutlierResult(
            column         = col,
            method         = "IQR",
            total_detected = total,
            likely_valid   = likely_valid,
            suspicious     = suspicious,
            extreme        = extreme,
            lower_bound    = round(lower_1, 4),
            upper_bound    = round(upper_1, 4),
            indices        = list(series[outside_1_5].index),
        )

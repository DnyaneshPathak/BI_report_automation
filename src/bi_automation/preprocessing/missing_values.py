"""
preprocessing/missing_values.py
---------------------------------
Analyses and imputes missing values according to column type.

Rules:
  - Continuous: median imputation (robust to outliers)
  - Categorical: mode or "Unknown"
  - Identifiers / Descriptive text: leave as-is
  - Logs every action taken
"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from preprocessing.datatype_detector import ColumnProfile

logger = logging.getLogger(__name__)

UNKNOWN_LABEL = "Unknown"


class MissingValueHandler:

    def __init__(self, df: pd.DataFrame, profiles: Dict[str, ColumnProfile]):
        self.df       = df.copy()
        self.profiles = profiles
        self.log: List[str] = []
        self.missing_summary: Dict[str, dict] = {}

    def analyse_and_impute(self) -> Tuple[pd.DataFrame, List[str], Dict[str, dict]]:
        self._build_missing_summary()
        self._impute()
        return self.df, self.log, self.missing_summary

    def _build_missing_summary(self) -> None:
        total = len(self.df)
        for col in self.df.columns:
            n_missing = self.df[col].isna().sum()
            self.missing_summary[col] = {
                "missing_count": int(n_missing),
                "missing_pct"  : round(n_missing / max(total, 1) * 100, 2),
            }

    def _impute(self) -> None:
        for col, profile in self.profiles.items():
            if col not in self.df.columns:
                continue
            n_missing = self.df[col].isna().sum()
            if n_missing == 0:
                continue

            atype = profile.analytical_type

            # Leave identifiers and free-text as-is
            if atype in ("identifier", "text") or not profile.include_in_analysis:
                continue

            # Numeric: median imputation
            if atype in ("continuous", "discrete_numeric"):
                median_val = self.df[col].median()
                if pd.notna(median_val):
                    self.df[col] = self.df[col].fillna(median_val)
                    self.log.append(
                        f"'{col}': imputed {n_missing} missing value(s) with median ({median_val:.2f})."
                    )

            # Categorical / binary: mode or "Unknown"
            elif atype in ("categorical_nominal", "categorical_ordinal", "binary"):
                mode_series = self.df[col].mode(dropna=True)
                if len(mode_series) > 0:
                    mode_val = mode_series.iloc[0]
                    self.df[col] = self.df[col].fillna(mode_val)
                    self.log.append(
                        f"'{col}': imputed {n_missing} missing value(s) with mode ('{mode_val}')."
                    )
                else:
                    self.df[col] = self.df[col].fillna(UNKNOWN_LABEL)
                    self.log.append(
                        f"'{col}': imputed {n_missing} missing value(s) with '{UNKNOWN_LABEL}'."
                    )

            # Datetime: leave as-is (replacing dates with medians is misleading)
            # else: no imputation

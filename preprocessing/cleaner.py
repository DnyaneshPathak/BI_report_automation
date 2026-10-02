"""
preprocessing/cleaner.py
--------------------------
Orchestrates data cleaning:
  - Text cleaning
  - Type correction
  - Missing-value handling
  - Duplicate removal
Keeps a preprocessing log of every decision made.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from preprocessing.datatype_detector import ColumnProfile

logger = logging.getLogger(__name__)

NULL_STRINGS = {
    "na", "n/a", "null", "none", "nil", "nan", "-", "--",
    "blank", "empty", "missing", "unknown", "#n/a", "#null!",
    "not available", "not applicable", "n.a.", "n.a",
}


class DataCleaner:
    """
    Cleans a DataFrame according to detected column profiles.
    Returns the cleaned DataFrame and a human-readable log.
    """

    def __init__(self, df: pd.DataFrame, profiles: Dict[str, ColumnProfile]):
        self.df       = df.copy()
        self.profiles = profiles
        self.log: List[str] = []

    # ── Public ────────────────────────────────────────────────────────────────
    def clean(self) -> Tuple[pd.DataFrame, List[str]]:
        self._standardize_column_names()
        self._replace_null_strings()
        self._correct_types()
        self._clean_text_columns()
        self._remove_exact_duplicates()
        return self.df, self.log

    # ── Steps ─────────────────────────────────────────────────────────────────
    def _standardize_column_names(self) -> None:
        renamed = {}
        for col in self.df.columns:
            clean = re.sub(r"\s+", " ", col.strip())
            if clean != col:
                renamed[col] = clean
        if renamed:
            self.df.rename(columns=renamed, inplace=True)
            self.log.append(f"Standardized {len(renamed)} column name(s).")

    def _replace_null_strings(self) -> None:
        count = 0
        for col in self.df.columns:
            mask = self.df[col].astype(str).str.strip().str.lower().isin(NULL_STRINGS)
            n = mask.sum()
            if n > 0:
                self.df.loc[mask, col] = np.nan
                count += n
        if count:
            self.log.append(f"Replaced {count} null-string sentinel value(s) with NaN.")

    def _correct_types(self) -> None:
        for col, profile in self.profiles.items():
            if col not in self.df.columns:
                continue
            series = self.df[col]

            if profile.analytical_type == "datetime":
                try:
                    converted = pd.to_datetime(series, infer_datetime_format=True, errors="coerce")
                    n_gained  = converted.notna().sum() - series.notna().sum()
                    self.df[col] = converted
                    if n_gained > 0:
                        self.log.append(f"'{col}': converted to datetime ({n_gained} newly parsed).")
                except Exception:
                    pass

            elif profile.analytical_type in ("continuous", "discrete_numeric",
                                              "financial_measure", "percentage"):
                cleaned = (
                    series.astype(str)
                    .str.replace(r"[₹$€£¥,\s%]", "", regex=True)
                    .str.strip()
                )
                numeric = pd.to_numeric(cleaned, errors="coerce")
                n_gained = numeric.notna().sum() - pd.to_numeric(series, errors="coerce").notna().sum()
                if n_gained > 0:
                    self.df[col] = numeric
                    self.log.append(f"'{col}': coerced to numeric ({n_gained} values converted).")
                elif pd.api.types.is_numeric_dtype(series):
                    pass  # already numeric
                else:
                    self.df[col] = numeric

            elif profile.analytical_type in ("categorical_nominal", "categorical_ordinal",
                                              "binary", "text"):
                self.df[col] = series.astype(str).str.strip()
                # Re-apply NaN where string is literally "nan"
                self.df.loc[self.df[col].str.lower() == "nan", col] = np.nan

    def _clean_text_columns(self) -> None:
        """Trim whitespace and remove invisible characters from string columns."""
        # Use chr() to avoid PyArrow regex issues with \\u escape sequences
        zero_width = "".join(chr(c) for c in [0x200B, 0x200C, 0x200D, 0xFEFF])
        for col in self.df.select_dtypes(include="object").columns:
            self.df[col] = (
                self.df[col]
                .astype(str)
                .str.strip()
                .str.translate(str.maketrans("", "", zero_width))
                .str.replace(r" +", " ", regex=True)
            )
            self.df.loc[self.df[col].str.lower() == "nan", col] = np.nan

    def _remove_exact_duplicates(self) -> None:
        """Remove 100% identical rows (clear technical duplicates only)."""
        before = len(self.df)
        self.df.drop_duplicates(inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        removed = before - len(self.df)
        if removed:
            self.log.append(f"Removed {removed} exact duplicate row(s).")

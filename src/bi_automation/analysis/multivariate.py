"""
analysis/multivariate.py
--------------------------
Finds meaningful 3-variable relationships for dashboard use.

Examples:
  Numeric × Categorical × Datetime  → trend by group over time
  Numeric × Categorical × Categorical → segment comparison

Only the most business-interpretable combinations are returned.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pandas as pd

from bi_automation.preprocessing.type_detector import ColumnProfile

logger = logging.getLogger(__name__)

MAX_MULTIVARIATE = 10


@dataclass
class MultivariateResult:
    description: str
    num_col: str
    cat_col: str
    time_col: Optional[str] = None
    cat2_col: Optional[str] = None
    # Aggregated table: {group_value: {period/cat2: agg_value}}
    pivot: Dict[str, Dict[str, float]] = field(default_factory=dict)
    insight: str = ""


class MultivariateAnalyser:

    def __init__(self, df: pd.DataFrame, profiles: Dict[str, ColumnProfile]):
        self.df       = df
        self.profiles = profiles

        self.numeric_cols = [
            c for c, p in profiles.items()
            if p.analytical_type in ("continuous", "discrete_numeric")
            and p.include_in_analysis and c in df.columns
        ]
        self.cat_cols = [
            c for c, p in profiles.items()
            if p.analytical_type in ("categorical_nominal", "categorical_ordinal")
            and p.include_in_analysis and c in df.columns
            and 2 <= df[c].nunique() <= 15
        ]
        self.date_cols = [
            c for c, p in profiles.items()
            if p.analytical_type == "datetime"
            and c in df.columns
        ]

    def analyse(self) -> List[MultivariateResult]:
        results: List[MultivariateResult] = []

        # Priority 1: Numeric × Category × Time
        for num in self.numeric_cols[:3]:
            for cat in self.cat_cols[:3]:
                for date in self.date_cols[:1]:
                    r = self._num_cat_time(num, cat, date)
                    if r:
                        results.append(r)
                    if len(results) >= MAX_MULTIVARIATE:
                        return results

        # Priority 2: Numeric × Category × Category
        if len(self.cat_cols) >= 2:
            for num in self.numeric_cols[:2]:
                for i, cat1 in enumerate(self.cat_cols[:4]):
                    for cat2 in self.cat_cols[i + 1: i + 3]:
                        r = self._num_cat_cat(num, cat1, cat2)
                        if r:
                            results.append(r)
                        if len(results) >= MAX_MULTIVARIATE:
                            return results

        return results

    # ── Numeric × Category × Time ─────────────────────────────────────────────
    def _num_cat_time(self, num: str, cat: str, date: str) -> Optional[MultivariateResult]:
        try:
            df_temp = self.df[[num, cat, date]].copy()
            df_temp[num] = pd.to_numeric(df_temp[num], errors="coerce")
            df_temp[date] = pd.to_datetime(df_temp[date], errors="coerce")
            df_temp = df_temp.dropna()
            if len(df_temp) < 20:
                return None

            df_temp["_period"] = df_temp[date].dt.to_period("M").astype(str)
            pivot = (
                df_temp.groupby([cat, "_period"])[num]
                .sum()
                .unstack(fill_value=0)
            )
            # Keep top 5 categories and last 24 periods
            top_cats = df_temp.groupby(cat)[num].sum().nlargest(5).index
            pivot = pivot.loc[pivot.index.isin(top_cats), pivot.columns[-24:]]

            pivot_dict = {
                str(row_key): {str(col_key): round(float(v), 2) for col_key, v in row.items()}
                for row_key, row in pivot.iterrows()
            }

            top_group = df_temp.groupby(cat)[num].sum().idxmax()
            return MultivariateResult(
                description=f"{num} by {cat} over Time",
                num_col=num, cat_col=cat, time_col=date,
                pivot=pivot_dict,
                insight=f"'{top_group}' generates the highest total '{num}' over time.",
            )
        except Exception as exc:
            logger.debug("multivariate num×cat×time failed for %s,%s,%s: %s", num, cat, date, exc)
            return None

    # ── Numeric × Category × Category ─────────────────────────────────────────
    def _num_cat_cat(self, num: str, cat1: str, cat2: str) -> Optional[MultivariateResult]:
        try:
            df_temp = self.df[[num, cat1, cat2]].copy()
            df_temp[num] = pd.to_numeric(df_temp[num], errors="coerce")
            df_temp = df_temp.dropna()
            if len(df_temp) < 20:
                return None

            pivot = df_temp.pivot_table(
                index=cat1, columns=cat2, values=num, aggfunc="sum", fill_value=0
            )
            # Keep top 5 × 5
            top_rows = df_temp.groupby(cat1)[num].sum().nlargest(5).index
            top_cols = df_temp.groupby(cat2)[num].sum().nlargest(5).index
            pivot = pivot.loc[pivot.index.isin(top_rows), [c for c in top_cols if c in pivot.columns]]

            pivot_dict = {
                str(r): {str(c): round(float(pivot.at[r, c]), 2) for c in pivot.columns}
                for r in pivot.index
            }

            return MultivariateResult(
                description=f"{num} by {cat1} and {cat2}",
                num_col=num, cat_col=cat1, cat2_col=cat2,
                pivot=pivot_dict,
                insight=f"'{num}' varies across both '{cat1}' and '{cat2}' dimensions.",
            )
        except Exception as exc:
            logger.debug("multivariate num×cat×cat failed for %s,%s,%s: %s", num, cat1, cat2, exc)
            return None

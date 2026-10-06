"""
analysis/statistical.py
------------------------
Runs appropriate statistical tests and computes confidence intervals.
Every test is validated for variable-type compatibility and sample size.
Results are explained in plain business language.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats

from bi_automation.preprocessing.type_detector import ColumnProfile
from bi_automation.profiling.profiler import ColumnStats

logger = logging.getLogger(__name__)


@dataclass
class StatTestResult:
    test_name: str
    column_a: str
    column_b: Optional[str]
    statistic: Optional[float]
    p_value: Optional[float]
    significant: bool
    conclusion: str
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None


class StatisticalAnalyser:

    def __init__(
        self,
        df: pd.DataFrame,
        profiles: Dict[str, ColumnProfile],
        col_stats: Dict[str, ColumnStats],
    ):
        self.df        = df
        self.profiles  = profiles
        self.col_stats = col_stats

    def analyse(self) -> List[StatTestResult]:
        results: List[StatTestResult] = []

        numeric_cols = [
            c for c, p in self.profiles.items()
            if p.analytical_type in ("continuous", "discrete_numeric")
            and p.include_in_analysis and c in self.df.columns
        ]
        cat_cols = [
            c for c, p in self.profiles.items()
            if p.analytical_type in ("categorical_nominal", "categorical_ordinal", "binary")
            and p.include_in_analysis and c in self.df.columns
            and 2 <= self.df[c].nunique() <= 15
        ]

        # --- Normality test for each numeric column ---
        for col in numeric_cols[:10]:
            r = self._normality_test(col)
            if r:
                results.append(r)

        # --- Confidence intervals for key numeric columns ---
        for col in numeric_cols[:6]:
            r = self._confidence_interval(col)
            if r:
                results.append(r)

        # --- ANOVA / Kruskal for numeric × categorical ---
        for num_col in numeric_cols[:3]:
            for cat_col in cat_cols[:3]:
                r = self._group_comparison_test(num_col, cat_col)
                if r:
                    results.append(r)

        return results

    # ── Normality (Shapiro-Wilk ≤5000 samples; else skip) ────────────────────
    def _normality_test(self, col: str) -> Optional[StatTestResult]:
        series = pd.to_numeric(self.df[col], errors="coerce").dropna()
        n = len(series)
        if n < 30 or n > 5000:
            return None
        try:
            stat, p = stats.shapiro(series.sample(min(n, 1000), random_state=42))
            sig = p < 0.05
            conclusion = (
                f"'{col}' does NOT follow a normal distribution (p={p:.4f})."
                if sig else
                f"'{col}' is approximately normally distributed (p={p:.4f})."
            )
            return StatTestResult(
                test_name="Shapiro-Wilk Normality",
                column_a=col, column_b=None,
                statistic=round(float(stat), 4),
                p_value=round(float(p), 4),
                significant=sig,
                conclusion=conclusion,
            )
        except Exception:
            return None

    # ── 95% Confidence Interval for mean ─────────────────────────────────────
    def _confidence_interval(self, col: str) -> Optional[StatTestResult]:
        series = pd.to_numeric(self.df[col], errors="coerce").dropna()
        n = len(series)
        if n < 30:
            return None
        mean = series.mean()
        se   = stats.sem(series)
        ci   = stats.t.interval(0.95, df=n - 1, loc=mean, scale=se)
        return StatTestResult(
            test_name="95% Confidence Interval (Mean)",
            column_a=col, column_b=None,
            statistic=round(float(mean), 4),
            p_value=None,
            significant=False,
            conclusion=(
                f"We are 95% confident the true mean of '{col}' lies between "
                f"{ci[0]:.2f} and {ci[1]:.2f} (sample mean: {mean:.2f})."
            ),
            ci_lower=round(float(ci[0]), 4),
            ci_upper=round(float(ci[1]), 4),
        )

    # ── Group comparison ──────────────────────────────────────────────────────
    def _group_comparison_test(self, num_col: str, cat_col: str) -> Optional[StatTestResult]:
        df_temp = pd.DataFrame({
            "num": pd.to_numeric(self.df[num_col], errors="coerce"),
            "cat": self.df[cat_col].astype(str),
        }).dropna()
        if len(df_temp) < 30:
            return None

        groups = [g["num"].values for _, g in df_temp.groupby("cat") if len(g) >= 5]
        if len(groups) < 2:
            return None

        try:
            if len(groups) == 2:
                stat, p = stats.mannwhitneyu(*groups, alternative="two-sided")
                test_name = "Mann-Whitney U"
            else:
                stat, p = stats.kruskal(*groups)
                test_name = "Kruskal-Wallis"

            sig = p < 0.05
            conclusion = (
                f"'{num_col}' differs significantly across '{cat_col}' groups ({test_name}, p={p:.4f})."
                if sig else
                f"No statistically significant difference in '{num_col}' across '{cat_col}' groups (p={p:.4f})."
            )
            return StatTestResult(
                test_name=test_name,
                column_a=num_col, column_b=cat_col,
                statistic=round(float(stat), 4),
                p_value=round(float(p), 4),
                significant=sig,
                conclusion=conclusion,
            )
        except Exception:
            return None

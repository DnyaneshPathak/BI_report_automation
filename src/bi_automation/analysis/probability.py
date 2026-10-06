"""
analysis/probability.py
------------------------
Computes empirical and conditional probabilities from the data.

Examples produced:
  P(Status = Cancelled) = 0.14
  P(Channel = Online | Region = West) = 0.43
  P(High Revenue) (above 75th percentile) = 0.25

No distribution is forced on data unless evidence supports it.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats

from bi_automation.preprocessing.type_detector import ColumnProfile

logger = logging.getLogger(__name__)

MAX_PROB_RESULTS = 20


@dataclass
class ProbabilityResult:
    description: str
    probability: float
    formula: str
    category: str    # empirical | conditional | percentile


class ProbabilityAnalyser:

    def __init__(self, df: pd.DataFrame, profiles: Dict[str, ColumnProfile]):
        self.df       = df
        self.profiles = profiles
        self.n_rows   = len(df)

    def analyse(self) -> List[ProbabilityResult]:
        results: List[ProbabilityResult] = []

        cat_cols = [
            c for c, p in self.profiles.items()
            if p.analytical_type in ("categorical_nominal", "categorical_ordinal", "binary")
            and p.include_in_analysis and c in self.df.columns
            and 2 <= self.df[c].nunique() <= 15
        ]
        num_cols = [
            c for c, p in self.profiles.items()
            if p.analytical_type in ("continuous", "discrete_numeric")
            and p.include_in_analysis and c in self.df.columns
        ]

        # Empirical probabilities for categorical columns
        for col in cat_cols[:5]:
            results.extend(self._empirical_cat(col))
            if len(results) >= MAX_PROB_RESULTS:
                return results

        # Conditional probabilities: cat1 given cat2
        if len(cat_cols) >= 2:
            for i, c1 in enumerate(cat_cols[:3]):
                for c2 in cat_cols[i + 1: i + 2]:
                    results.extend(self._conditional_cat(c1, c2))
                    if len(results) >= MAX_PROB_RESULTS:
                        return results

        # Percentile-based probability for numeric columns
        for col in num_cols[:3]:
            results.extend(self._percentile_prob(col))
            if len(results) >= MAX_PROB_RESULTS:
                return results

        return results[:MAX_PROB_RESULTS]

    # ── Empirical probability ─────────────────────────────────────────────────
    def _empirical_cat(self, col: str) -> List[ProbabilityResult]:
        valid = self.df[col].dropna().astype(str)
        n_total = len(valid)
        if n_total == 0:
            return []
        freq = valid.value_counts()
        results = []
        for val, cnt in freq.head(5).items():
            prob = round(cnt / n_total, 4)
            results.append(ProbabilityResult(
                description=f"P({col} = {val})",
                probability=prob,
                formula=f"{cnt} / {n_total}",
                category="empirical",
            ))
        return results

    # ── Conditional probability ───────────────────────────────────────────────
    def _conditional_cat(self, col_a: str, col_b: str) -> List[ProbabilityResult]:
        df_temp = self.df[[col_a, col_b]].dropna().astype(str)
        if len(df_temp) < 30:
            return []
        results = []
        # Take top category of col_a, top 2 of col_b
        top_a = df_temp[col_a].value_counts().index[0]
        top_bs = df_temp[col_b].value_counts().index[:2]
        for bval in top_bs:
            sub   = df_temp[df_temp[col_b] == bval]
            n_sub = len(sub)
            if n_sub < 5:
                continue
            cnt  = (sub[col_a] == top_a).sum()
            prob = round(cnt / n_sub, 4)
            results.append(ProbabilityResult(
                description=f"P({col_a} = {top_a} | {col_b} = {bval})",
                probability=prob,
                formula=f"{cnt} / {n_sub}",
                category="conditional",
            ))
        return results

    # ── Percentile-based (high / low buckets) ─────────────────────────────────
    def _percentile_prob(self, col: str) -> List[ProbabilityResult]:
        numeric = pd.to_numeric(self.df[col], errors="coerce").dropna()
        if len(numeric) < 10:
            return []
        n_total = len(numeric)
        p75 = float(np.percentile(numeric, 75))
        p25 = float(np.percentile(numeric, 25))
        high_cnt = int((numeric > p75).sum())
        low_cnt  = int((numeric < p25).sum())
        return [
            ProbabilityResult(
                description=f"P(High {col}) — above 75th percentile ({p75:.2f})",
                probability=round(high_cnt / n_total, 4),
                formula=f"{high_cnt} / {n_total}",
                category="percentile",
            ),
            ProbabilityResult(
                description=f"P(Low {col}) — below 25th percentile ({p25:.2f})",
                probability=round(low_cnt / n_total, 4),
                formula=f"{low_cnt} / {n_total}",
                category="percentile",
            ),
        ]

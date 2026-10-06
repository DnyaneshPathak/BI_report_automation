"""
analysis/bivariate.py
----------------------
Performs bivariate analysis between eligible column pairs.

Pairs analysed (auto-selected):
  Numeric × Numeric   → Pearson / Spearman correlation, scatter data
  Numeric × Categorical → Group statistics, optional statistical tests
  Categorical × Categorical → Chi-square, Cramer's V, cross-tab

Only statistically meaningful and interpretable pairs are returned.
"""

from __future__ import annotations

import itertools
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from bi_automation.preprocessing.type_detector import ColumnProfile

logger = logging.getLogger(__name__)

MAX_PAIRS = 50    # cap expensive pairwise analysis


@dataclass
class BivariatePair:
    col_a: str
    col_b: str
    pair_type: str                       # num_num | num_cat | cat_cat
    # Numeric × Numeric
    pearson_r: Optional[float] = None
    pearson_p: Optional[float] = None
    spearman_r: Optional[float] = None
    spearman_p: Optional[float] = None
    correlation_strength: str = ""       # strong | moderate | weak | none
    # Numeric × Categorical
    group_means: Dict[str, float] = field(default_factory=dict)
    group_medians: Dict[str, float] = field(default_factory=dict)
    group_stds: Dict[str, float] = field(default_factory=dict)
    group_counts: Dict[str, int] = field(default_factory=dict)
    stat_test: str = ""
    stat_p_value: Optional[float] = None
    stat_significant: Optional[bool] = None
    # Categorical × Categorical
    cramers_v: Optional[float] = None
    chi_sq_p: Optional[float] = None
    cross_tab: Dict[str, Dict[str, int]] = field(default_factory=dict)
    # Shared
    insight: str = ""


class BivariateAnalyser:

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
            if p.analytical_type in ("categorical_nominal", "categorical_ordinal", "binary")
            and p.include_in_analysis and c in df.columns
            and df[c].nunique() <= 30   # skip high-cardinality categoricals
        ]

    def analyse(self) -> List[BivariatePair]:
        pairs: List[BivariatePair] = []

        # --- Numeric × Numeric ---
        for ca, cb in itertools.combinations(self.numeric_cols, 2):
            if len(pairs) >= MAX_PAIRS:
                break
            p = self._num_num(ca, cb)
            if p:
                pairs.append(p)

        # --- Numeric × Categorical ---
        analysed = 0
        for num_col in self.numeric_cols:
            for cat_col in self.cat_cols:
                if analysed >= MAX_PAIRS:
                    break
                p = self._num_cat(num_col, cat_col)
                if p:
                    pairs.append(p)
                    analysed += 1

        # --- Categorical × Categorical ---
        for ca, cb in itertools.combinations(self.cat_cols[:10], 2):
            if len(pairs) >= MAX_PAIRS * 2:
                break
            p = self._cat_cat(ca, cb)
            if p:
                pairs.append(p)

        # Sort by insight strength (correlation / cramer's v)
        pairs.sort(key=lambda x: abs(x.pearson_r or x.cramers_v or 0), reverse=True)
        return pairs

    # ── Numeric × Numeric ─────────────────────────────────────────────────────
    def _num_num(self, ca: str, cb: str) -> Optional[BivariatePair]:
        a = pd.to_numeric(self.df[ca], errors="coerce")
        b = pd.to_numeric(self.df[cb], errors="coerce")
        mask = a.notna() & b.notna()
        a, b = a[mask], b[mask]
        if len(a) < 10:
            return None

        pair = BivariatePair(col_a=ca, col_b=cb, pair_type="num_num")
        try:
            r, p = stats.pearsonr(a, b)
            pair.pearson_r = round(float(r), 4)
            pair.pearson_p = round(float(p), 4)
        except Exception:
            pass
        try:
            sr, sp = stats.spearmanr(a, b)
            pair.spearman_r = round(float(sr), 4)
            pair.spearman_p = round(float(sp), 4)
        except Exception:
            pass

        r_val = abs(pair.pearson_r or 0)
        if r_val >= 0.7:
            pair.correlation_strength = "strong"
            direction = "positive" if (pair.pearson_r or 0) > 0 else "negative"
            pair.insight = (
                f"A strong {direction} correlation (r={pair.pearson_r}) exists "
                f"between '{ca}' and '{cb}'."
            )
        elif r_val >= 0.3:
            pair.correlation_strength = "moderate"
        else:
            pair.correlation_strength = "weak"

        return pair

    # ── Numeric × Categorical ─────────────────────────────────────────────────
    def _num_cat(self, num_col: str, cat_col: str) -> Optional[BivariatePair]:
        numeric = pd.to_numeric(self.df[num_col], errors="coerce")
        category = self.df[cat_col].astype(str)

        df_temp = pd.DataFrame({"num": numeric, "cat": category}).dropna()
        if len(df_temp) < 30:
            return None

        groups = df_temp.groupby("cat")["num"]
        group_means   = groups.mean().round(4).to_dict()
        group_medians = groups.median().round(4).to_dict()
        group_stds    = groups.std().round(4).fillna(0).to_dict()
        group_counts  = groups.count().to_dict()

        if len(group_means) < 2:
            return None

        pair = BivariatePair(
            col_a=num_col, col_b=cat_col, pair_type="num_cat",
            group_means   = {str(k): float(v) for k, v in group_means.items()},
            group_medians = {str(k): float(v) for k, v in group_medians.items()},
            group_stds    = {str(k): float(v) for k, v in group_stds.items()},
            group_counts  = {str(k): int(v)   for k, v in group_counts.items()},
        )

        # Statistical test
        group_data = [g.values for _, g in df_temp.groupby("cat")["num"] if len(g) >= 5]
        if len(group_data) >= 2:
            if len(group_data) == 2:
                _, p = stats.mannwhitneyu(*group_data, alternative="two-sided")
                pair.stat_test = "Mann-Whitney U"
            else:
                _, p = stats.kruskal(*group_data)
                pair.stat_test = "Kruskal-Wallis"
            pair.stat_p_value    = round(float(p), 4)
            pair.stat_significant = p < 0.05

            if pair.stat_significant:
                max_cat  = max(group_means, key=group_means.get)
                min_cat  = min(group_means, key=group_means.get)
                pair.insight = (
                    f"'{num_col}' differs significantly across '{cat_col}' groups "
                    f"(p={pair.stat_p_value}). "
                    f"'{max_cat}' has the highest mean ({group_means[max_cat]:.2f}) "
                    f"and '{min_cat}' has the lowest ({group_means[min_cat]:.2f})."
                )
        return pair

    # ── Categorical × Categorical ─────────────────────────────────────────────
    def _cat_cat(self, ca: str, cb: str) -> Optional[BivariatePair]:
        df_temp = self.df[[ca, cb]].dropna().astype(str)
        if len(df_temp) < 30:
            return None

        ct = pd.crosstab(df_temp[ca], df_temp[cb])
        if ct.shape[0] < 2 or ct.shape[1] < 2:
            return None

        pair = BivariatePair(col_a=ca, col_b=cb, pair_type="cat_cat")

        try:
            chi2, p, dof, _ = stats.chi2_contingency(ct)
            pair.chi_sq_p = round(float(p), 4)
            # Cramer's V
            n = ct.values.sum()
            k = min(ct.shape) - 1
            v = np.sqrt(chi2 / (n * k)) if n * k > 0 else 0
            pair.cramers_v = round(float(v), 4)
        except Exception:
            return None

        # Top 5 × 5 cross-tab for display
        top_rows = ct.sum(axis=1).nlargest(5).index
        top_cols = ct.sum(axis=0).nlargest(5).index
        ct_small = ct.loc[top_rows, top_cols]
        pair.cross_tab = {str(r): {str(c): int(ct_small.at[r, c]) for c in top_cols} for r in top_rows}

        if pair.cramers_v and pair.cramers_v > 0.3:
            pair.insight = (
                f"A notable association exists between '{ca}' and '{cb}' "
                f"(Cramér's V={pair.cramers_v})."
            )
        return pair

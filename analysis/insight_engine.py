"""
analysis/insight_engine.py
---------------------------
Generates ranked, plain-language business insights.

Every numerical claim is derived from calculated results.
No hallucination — every insight references a computed statistic.

Also computes the Analytical Relevance Score per column
(used for dashboard prioritisation — NOT machine learning).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from preprocessing.datatype_detector import ColumnProfile
from analysis.profiler import ColumnStats
from analysis.bivariate import BivariatePair
from analysis.multivariate import MultivariateResult

logger = logging.getLogger(__name__)


@dataclass
class Insight:
    text: str
    priority: int = 5      # 1 = highest, 10 = lowest
    category: str = "general"   # trend | comparison | correlation | distribution | quality


@dataclass
class AnalyticalRelevanceScore:
    column: str
    score: float
    reasons: List[str] = field(default_factory=list)


class InsightEngine:

    def __init__(
        self,
        df: pd.DataFrame,
        profiles: Dict[str, ColumnProfile],
        col_stats: Dict[str, ColumnStats],
        bivariate_pairs: List[BivariatePair],
        multivariate_results: List[MultivariateResult],
    ):
        self.df                   = df
        self.profiles             = profiles
        self.col_stats            = col_stats
        self.bivariate_pairs      = bivariate_pairs
        self.multivariate_results = multivariate_results
        self.n_rows               = len(df)

    # ── Main entry-point ──────────────────────────────────────────────────────
    def generate_insights(self) -> List[Insight]:
        insights: List[Insight] = []
        insights += self._trend_insights()
        insights += self._comparison_insights()
        insights += self._correlation_insights()
        insights += self._distribution_insights()
        insights += self._multivariate_insights()
        # Sort by priority
        insights.sort(key=lambda x: x.priority)
        return insights[:20]   # top 20 most important

    def compute_relevance_scores(self) -> List[AnalyticalRelevanceScore]:
        scores: List[AnalyticalRelevanceScore] = []
        for col, profile in self.profiles.items():
            if not profile.include_in_analysis or col not in self.col_stats:
                continue
            cs = self.col_stats[col]
            score = 0.0
            reasons = []

            # Completeness
            completeness = 1 - cs.missing_pct / 100
            score += completeness * 20
            if completeness > 0.95:
                reasons.append("High data completeness")

            # Variance (for numerics)
            if cs.cv is not None:
                if cs.cv > 30:
                    score += 20
                    reasons.append("High coefficient of variation")
                elif cs.cv > 10:
                    score += 10

            # Cardinality (for categoricals) — sweet spot 3–20
            if cs.unique_count:
                if 3 <= cs.unique_count <= 20:
                    score += 15
                    reasons.append("Good categorical cardinality for grouping")
                elif cs.unique_count > 100:
                    score -= 5

            # Role bonuses
            if profile.feature_role in ("Financial Measure", "Target-Like Metric"):
                score += 20
                reasons.append("Financial / target metric")
            elif profile.feature_role in ("Measure", "Quantity"):
                score += 10
            elif profile.feature_role == "Time Dimension":
                score += 15
                reasons.append("Time dimension enables trend analysis")
            elif profile.feature_role in ("Dimension", "Category", "Location"):
                score += 12

            scores.append(AnalyticalRelevanceScore(
                column=col,
                score=round(score, 2),
                reasons=reasons,
            ))

        scores.sort(key=lambda x: x.score, reverse=True)
        return scores

    # ── Trend insights (datetime columns) ────────────────────────────────────
    def _trend_insights(self) -> List[Insight]:
        insights = []
        date_cols = [c for c, p in self.profiles.items() if p.analytical_type == "datetime" and c in self.df.columns]
        num_cols  = [
            c for c, p in self.profiles.items()
            if p.analytical_type in ("continuous", "discrete_numeric")
            and p.include_in_analysis and c in self.df.columns
        ]

        for date_col in date_cols[:1]:
            for num_col in num_cols[:2]:
                try:
                    df_temp = pd.DataFrame({
                        "dt" : pd.to_datetime(self.df[date_col], errors="coerce"),
                        "val": pd.to_numeric(self.df[num_col], errors="coerce"),
                    }).dropna()
                    if len(df_temp) < 10:
                        continue
                    df_temp["year"] = df_temp["dt"].dt.year
                    yearly = df_temp.groupby("year")["val"].sum()
                    if len(yearly) >= 2:
                        first_val = yearly.iloc[0]
                        last_val  = yearly.iloc[-1]
                        if first_val != 0:
                            growth = (last_val - first_val) / abs(first_val) * 100
                            direction = "increased" if growth > 0 else "decreased"
                            insights.append(Insight(
                                text=(
                                    f"'{num_col}' {direction} by {abs(growth):.1f}% "
                                    f"from {yearly.index[0]} to {yearly.index[-1]}."
                                ),
                                priority=1,
                                category="trend",
                            ))
                except Exception:
                    pass
        return insights

    # ── Comparison insights (numeric by category) ─────────────────────────────
    def _comparison_insights(self) -> List[Insight]:
        insights = []
        for pair in self.bivariate_pairs:
            if pair.pair_type == "num_cat" and pair.stat_significant and pair.insight:
                insights.append(Insight(
                    text=pair.insight,
                    priority=2,
                    category="comparison",
                ))
            if len(insights) >= 6:
                break
        return insights

    # ── Correlation insights ──────────────────────────────────────────────────
    def _correlation_insights(self) -> List[Insight]:
        insights = []
        for pair in self.bivariate_pairs:
            if pair.pair_type == "num_num" and pair.correlation_strength == "strong" and pair.insight:
                insights.append(Insight(
                    text=pair.insight,
                    priority=2,
                    category="correlation",
                ))
            if len(insights) >= 4:
                break
        return insights

    # ── Distribution insights ─────────────────────────────────────────────────
    def _distribution_insights(self) -> List[Insight]:
        insights = []
        for col, cs in self.col_stats.items():
            profile = self.profiles.get(col)
            if not profile or not profile.include_in_analysis:
                continue

            # Top category insight
            if cs.top_category and cs.freq_distribution:
                top_pct = list(cs.freq_distribution.values())[0]
                if top_pct > 30:
                    insights.append(Insight(
                        text=(
                            f"'{cs.top_category}' is the dominant category in '{col}', "
                            f"representing approximately {top_pct:.1f}% of records."
                        ),
                        priority=3,
                        category="distribution",
                    ))

            # Outlier insight
            if cs.outlier_count and cs.outlier_count > 5:
                insights.append(Insight(
                    text=(
                        f"'{col}' contains {cs.outlier_count} potential outlier(s) "
                        f"(outside 1.5×IQR). These may warrant further investigation."
                    ),
                    priority=6,
                    category="distribution",
                ))

            if len(insights) >= 5:
                break
        return insights

    # ── Multivariate insights ─────────────────────────────────────────────────
    def _multivariate_insights(self) -> List[Insight]:
        insights = []
        for mv in self.multivariate_results:
            if mv.insight:
                insights.append(Insight(
                    text=mv.insight,
                    priority=3,
                    category="comparison",
                ))
        return insights

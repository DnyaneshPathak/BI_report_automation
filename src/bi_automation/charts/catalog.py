"""
dashboard/chart_selector.py
----------------------------
Selects appropriate chart types for each analysis result.

Follows strict rules:
  Trends      → Line Chart / Area Chart
  Category    → Bar / Column Chart
  Ranking     → Horizontal Bar
  Part-Whole  → Treemap / Stacked Bar (Donut only ≤ 6 categories)
  Relationship→ Scatter Plot
  Distribution→ Histogram
  Geographic  → Map (local PBI only)
  Detail      → Table / Matrix
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from bi_automation.preprocessing.type_detector import ColumnProfile
from bi_automation.profiling.profiler import ColumnStats
from bi_automation.analysis.univariate import UnivariateResult
from bi_automation.analysis.bivariate import BivariatePair
from bi_automation.analysis.multivariate import MultivariateResult
from bi_automation.analysis.insights import AnalyticalRelevanceScore

logger = logging.getLogger(__name__)

MAX_DONUT_CATEGORIES = 6


from bi_automation.models.domain import VisualSpec
class ChartSelector:

    def __init__(
        self,
        profiles: Dict[str, ColumnProfile],
        col_stats: Dict[str, ColumnStats],
        univariate_results: Dict[str, UnivariateResult],
        bivariate_pairs: List[BivariatePair],
        multivariate_results: List[MultivariateResult],
        relevance_scores: List[AnalyticalRelevanceScore],
    ):
        self.profiles             = profiles
        self.col_stats            = col_stats
        self.univariate_results   = univariate_results
        self.bivariate_pairs      = bivariate_pairs
        self.multivariate_results = multivariate_results
        # Build relevance lookup
        self.relevance = {s.column: s.score for s in relevance_scores}

    def select(self) -> List[VisualSpec]:
        specs: List[VisualSpec] = []

        specs += self._trend_charts()
        specs += self._category_charts()
        specs += self._numeric_distribution_charts()
        specs += self._correlation_charts()
        specs += self._grouped_charts()
        specs += self._multivariate_charts()

        # Sort by priority, cap total
        specs.sort(key=lambda s: s.priority)
        # Limit per page
        return self._apply_page_limits(specs)

    # ── Trend charts ──────────────────────────────────────────────────────────
    def _trend_charts(self) -> List[VisualSpec]:
        specs = []
        for col, res in self.univariate_results.items():
            if res.analytical_type != "datetime" or not res.trend_by_month:
                continue
            labels = list(res.trend_by_month.keys())[-24:]
            values = [res.trend_by_month[k] for k in labels]
            specs.append(VisualSpec(
                id  = f"trend_month_{col}",
                chart_type= "line",
                title     = f"Monthly Trend — {col}",
                dimension  = col,
                measure  = "Count",
                data      = {"labels": labels, "values": values},
                page      = 3,
                priority  = 2,
                reason    = "Datetime column: monthly trend is most informative.",
            ))
            break  # one primary trend chart
        return specs

    # ── Category charts ───────────────────────────────────────────────────────
    def _category_charts(self) -> List[VisualSpec]:
        specs = []
        rel_sorted = sorted(
            [(c, s) for c, s in self.relevance.items()
             if self.profiles.get(c) and
             self.profiles[c].analytical_type in ("categorical_nominal", "categorical_ordinal")
             and c in self.univariate_results],
            key=lambda x: x[1], reverse=True
        )
        for col, score in rel_sorted[:4]:
            res  = self.univariate_results[col]
            n_cats = len(res.category_labels)
            if n_cats == 0:
                continue

            if n_cats <= 4:
                ctype = "pie"
            elif n_cats <= MAX_DONUT_CATEGORIES:
                ctype = "donut"
            elif n_cats <= 15:
                ctype = "bar"
            else:
                ctype = "treemap"

            page = 1 if score > 30 else 2
            specs.append(VisualSpec(
                id  = f"cat_{col}",
                chart_type= ctype,
                title     = f"{col.replace('_',' ').title()} Distribution",
                dimension  = col,
                measure  = "Count",
                data      = {
                    "labels": res.category_labels[:15],
                    "values": res.category_counts[:15],
                },
                page      = page,
                priority  = 3 if page == 1 else 5,
                reason    = f"Categorical with {n_cats} categories → {ctype}.",
            ))
        return specs

    # ── Numeric distribution ──────────────────────────────────────────────────
    def _numeric_distribution_charts(self) -> List[VisualSpec]:
        specs = []
        rel_sorted = sorted(
            [(c, s) for c, s in self.relevance.items()
             if self.profiles.get(c) and
             self.profiles[c].analytical_type in ("continuous", "discrete_numeric")
             and c in self.univariate_results],
            key=lambda x: x[1], reverse=True
        )
        for col, score in rel_sorted[:3]:
            res = self.univariate_results[col]
            if not res.histogram_bins:
                continue
            # Build histogram bar data from bins
            bin_labels = [
                f"{res.histogram_bins[i]:.1f}–{res.histogram_bins[i+1]:.1f}"
                for i in range(len(res.histogram_counts))
            ]
            specs.append(VisualSpec(
                id  = f"hist_{col}",
                chart_type= "histogram",
                title     = f"{col.replace('_',' ').title()} Distribution",
                dimension  = col,
                measure  = "Frequency",
                data      = {"labels": bin_labels, "values": res.histogram_counts},
                page      = 4,
                priority  = 6,
                reason    = "Numeric distribution → histogram.",
            ))
        return specs

    # ── Correlation charts ────────────────────────────────────────────────────
    def _correlation_charts(self) -> List[VisualSpec]:
        specs = []
        strong_pairs = [
            p for p in self.bivariate_pairs
            if p.pair_type == "num_num" and p.correlation_strength == "strong"
        ]
        for pair in strong_pairs[:2]:
            specs.append(VisualSpec(
                id  = f"scatter_{pair.col_a}_{pair.col_b}",
                chart_type= "scatter",
                title     = f"{pair.col_a} vs {pair.col_b}",
                dimension  = pair.col_a,
                measure  = pair.col_b,
                data      = {"pearson_r": pair.pearson_r},
                page      = 4,
                priority  = 5,
                reason    = f"Strong correlation r={pair.pearson_r}.",
            ))
        return specs

    # ── Grouped bar charts (numeric by category) ──────────────────────────────
    def _grouped_charts(self) -> List[VisualSpec]:
        specs = []
        sig_pairs = [
            p for p in self.bivariate_pairs
            if p.pair_type == "num_cat" and p.stat_significant and p.group_means
        ]
        for pair in sig_pairs[:3]:
            cats   = list(pair.group_means.keys())[:15]
            values = [pair.group_means[c] for c in cats]
            page   = 1 if len(specs) == 0 else 2
            specs.append(VisualSpec(
                id  = f"grouped_{pair.col_a}_{pair.col_b}",
                chart_type= "bar",
                title     = f"Avg {pair.col_a} by {pair.col_b}",
                dimension  = pair.col_b,
                measure  = pair.col_a,
                data      = {"labels": cats, "values": values},
                page      = page,
                priority  = 2,
                reason    = f"Significant difference across {pair.col_b} groups.",
            ))
        return specs

    # ── Multivariate ──────────────────────────────────────────────────────────
    def _multivariate_charts(self) -> List[VisualSpec]:
        specs = []
        for mv in self.multivariate_results:
            # Only include if the numeric and primary categorical column are statistically related
            pair = next((p for p in self.bivariate_pairs 
                         if (p.col_a == mv.num_col and p.col_b == mv.cat_col) or 
                            (p.col_b == mv.num_col and p.col_a == mv.cat_col)), None)
            
            if pair and hasattr(pair, 'stat_significant') and not pair.stat_significant:
                continue # Skip unrelated attributes
                
            if mv.time_col:
                # Stacked line per category
                specs.append(VisualSpec(
                    id  = f"mv_{mv.num_col}_{mv.cat_col}_time",
                    chart_type= "multi_line",
                    title     = f"{mv.num_col} by {mv.cat_col} Over Time",
                    dimension  = mv.time_col,
                    measure  = mv.num_col,
                    group_column = mv.cat_col,
                    data      = mv.pivot,
                    page      = 3,
                    priority  = 3,
                    reason    = "Numeric × Category × Time trend.",
                ))
            else:
                specs.append(VisualSpec(
                    id  = f"mv_{mv.num_col}_{mv.cat_col}",
                    chart_type= "stacked_bar",
                    title     = f"{mv.num_col} by {mv.cat_col} and {mv.cat2_col}",
                    dimension  = mv.cat_col,
                    measure  = mv.num_col,
                    group_column = mv.cat2_col,
                    data      = mv.pivot,
                    page      = 2,
                    priority  = 4,
                    reason    = "Numeric × Category × Category analysis.",
                ))
            
            if len(specs) >= 2:
                break
                
        return specs

    # ── Limit per page ────────────────────────────────────────────────────────
    def _apply_page_limits(self, specs: List[VisualSpec]) -> List[VisualSpec]:
        page_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        result = []
        for spec in specs:
            page = spec.page if spec.page in page_counts else 2
            if page_counts[page] < 7:
                result.append(spec)
                page_counts[page] += 1
        return result

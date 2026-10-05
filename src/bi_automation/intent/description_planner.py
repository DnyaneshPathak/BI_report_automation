"""
src/bi_automation/intent/description_planner.py
-------------------------------------------------
Phase 3 & 4: Description-Driven Dashboard Planner.

Takes the user's goal description (including per-column descriptions like
  "For Revenue: show trend over time | For Category: breakdown by region")
and the dataset profiles, then produces a list of VisualSpec objects
that directly reflect what the user asked for.

This is completely deterministic — no LLM, no external calls.
It uses the schema + user text to construct semantically meaningful charts.
"""

from __future__ import annotations

import logging
import re
import uuid
from typing import Dict, List, Optional, Tuple

import pandas as pd

from preprocessing.datatype_detector import ColumnProfile
from analysis.profiler import ColumnStats
from analysis.univariate import UnivariateResult
from analysis.bivariate import BivariatePair
from bi_automation.models.domain import VisualSpec

logger = logging.getLogger(__name__)


# ── Keyword → chart-type intent mapping ───────────────────────────────────────
_INTENT_MAP: List[Tuple[re.Pattern, str, str]] = [
    # pattern, chart_type, description
    (re.compile(r"\b(trend|over time|by month|time series|timeline|monthly|yearly|quarterly)\b", re.I), "line",        "Time-series trend"),
    (re.compile(r"\b(breakdown|by category|by segment|by region|by country|distribution across|split by)\b", re.I), "bar", "Category breakdown"),
    (re.compile(r"\b(distribution|histogram|frequency|how many|spread|range)\b", re.I), "histogram",  "Distribution"),
    (re.compile(r"\b(proportion|share|part[\- ]of[\- ]whole|percentage breakdown|composition)\b", re.I), "donut",   "Part-of-whole proportion"),
    (re.compile(r"\b(correlation|vs|versus|relationship between|compare .+ and|scatter)\b", re.I),  "scatter",    "Correlation/relationship"),
    (re.compile(r"\b(top|rank|highest|lowest|best|worst|leading)\b", re.I),                          "bar",        "Ranking"),
    (re.compile(r"\b(cumulative|running total|growth|progression)\b", re.I),                         "area",       "Cumulative/growth"),
    (re.compile(r"\b(map|geographic|by country|by state|by city|regional)\b", re.I),                 "map",        "Geographic"),
    (re.compile(r"\b(heat|matrix|cross tab|pivot)\b", re.I),                                          "heatmap",    "Heatmap/matrix"),
    (re.compile(r"\b(kpi|total|sum|aggregate|overall|grand total)\b", re.I),                          "kpi",        "KPI metric"),
]

# Aggregation keyword mapping
_AGG_MAP = {
    "total": "sum", "sum": "sum", "average": "mean", "avg": "mean",
    "mean": "mean", "count": "count", "distinct": "count",
    "max": "max", "maximum": "max", "min": "min", "minimum": "min",
    "median": "median",
}


class DescriptionPlanner:
    """
    Parses user goal descriptions and produces concrete VisualSpec lists.
    """

    def __init__(
        self,
        profiles: Dict[str, ColumnProfile],
        col_stats: Dict[str, ColumnStats],
        univariate: Dict[str, UnivariateResult],
        bivariate: List[BivariatePair],
        df: pd.DataFrame,
    ):
        self.profiles = profiles
        self.col_stats = col_stats
        self.univariate = univariate
        self.bivariate = bivariate
        self.df = df

        # Build fast lookup structures
        self._col_lower: Dict[str, str] = {c.lower(): c for c in profiles}
        for c in profiles:
            no_parens = re.sub(r'\(.*?\)', '', c).strip().lower()
            if no_parens and no_parens not in self._col_lower:
                self._col_lower[no_parens] = c
                
        self._measures = [c for c, p in profiles.items()
                          if p.analytical_type in ("continuous", "discrete_numeric")]
        self._dimensions = [c for c, p in profiles.items()
                            if p.analytical_type in ("categorical_nominal", "categorical_ordinal", "binary")]
        self._dates = [c for c, p in profiles.items()
                       if p.analytical_type == "datetime"]
        self._identifiers = [c for c, p in profiles.items()
                              if p.analytical_type == "identifier"]

    # ── Public API ────────────────────────────────────────────────────────────

    def plan(self, goal_description: str) -> List[VisualSpec]:
        """
        Parse the full goal description and return an ordered list of VisualSpecs.
        Falls back to auto-planning if no description-driven specs are found.
        """
        if not goal_description or not goal_description.strip():
            return self._auto_plan()

        # Parse per-feature blocks separated by " | "
        blocks = [b.strip() for b in goal_description.split("|") if b.strip()]
        all_specs: List[VisualSpec] = []
        global_text = ""

        for block in blocks:
            # Detect "For ColumnName: <instructions>"
            m = re.match(r"^[Ff]or\s+(.+?):\s*(.+)$", block, re.S)
            if m:
                col_hint = m.group(1).strip()
                instructions = m.group(2).strip()
                col = self._resolve_column(col_hint)
                specs = self._specs_from_instructions(instructions, primary_col=col)
                all_specs.extend(specs)
            else:
                global_text += " " + block

        # Handle global (non-per-feature) instructions by splitting into logical sentences
        if global_text.strip():
            sentences = re.split(r'[.,;!]+|\band\b', global_text)
            for sentence in sentences:
                if sentence.strip():
                    global_specs = self._specs_from_instructions(sentence.strip())
                    all_specs.extend(global_specs)

        # De-duplicate by id
        seen_ids = set()
        unique_specs = []
        for s in all_specs:
            if s.id not in seen_ids:
                seen_ids.add(s.id)
                unique_specs.append(s)

        if not unique_specs:
            logger.info("No description-driven specs found — falling back to auto_plan()")
            return self._auto_plan()

        # Assign priorities based on order
        for i, s in enumerate(unique_specs):
            s.priority = i + 1

        logger.info("Description planner produced %d visuals", len(unique_specs))
        return unique_specs

    # ── Per-instruction parser ────────────────────────────────────────────────

    def _specs_from_instructions(
        self, text: str, primary_col: Optional[str] = None
    ) -> List[VisualSpec]:
        specs = []
        matched_intents = set()

        for pattern, chart_type, desc in _INTENT_MAP:
            if pattern.search(text):
                if chart_type in matched_intents:
                    continue
                matched_intents.add(chart_type)

                if chart_type == "kpi":
                    # KPI is handled elsewhere — skip visual
                    continue

                spec = self._build_for_intent(chart_type, text, primary_col)
                if spec:
                    specs.append(spec)
                    
        # If no specific chart intent matched, but we have a primary column, generate generic default charts for it
        if not specs and primary_col:
            specs.extend(self._auto_plan_for_column(primary_col))

        return specs

    def _build_for_intent(
        self, chart_type: str, text: str, primary_col: Optional[str]
    ) -> Optional[VisualSpec]:
        """
        Construct a VisualSpec for the detected chart_type.
        """
        agg = self._detect_aggregation(text)
        cols_in_text = self._find_columns_in_text(text)
        detected_col = primary_col or (cols_in_text[0] if cols_in_text else None)

        if chart_type == "line":
            date_col = self._dates[0] if self._dates else None
            measure = detected_col if detected_col and detected_col in self._measures else self._most_relevant_measure()
            if not date_col or not measure:
                return None
            return self._make_spec("line", title=f"{measure} over Time", dimension=date_col, measure=measure, aggregation=agg)

        elif chart_type == "bar":
            dim = detected_col if detected_col and detected_col in self._dimensions else self._most_relevant_dimension()
            measure = self._most_relevant_measure()
            if len(cols_in_text) >= 2:
                # If they mention two columns (e.g. "Sales by Region")
                for c in cols_in_text:
                    if c in self._measures: measure = c
                    if c in self._dimensions: dim = c
            if not dim or not measure:
                return None
            top_n = self._detect_top_n(text)
            return self._make_spec("bar", title=f"{measure} by {dim}", dimension=dim, measure=measure, aggregation=agg, top_n=top_n)

        elif chart_type == "histogram":
            if detected_col and detected_col in self._dimensions:
                return self._make_spec("bar", title=f"{detected_col} Distribution", dimension=detected_col, measure=None, aggregation="count")
            
            col = detected_col if detected_col and detected_col in self._measures else self._most_relevant_measure()
            if not col:
                return None
            return self._make_spec("histogram", title=f"Distribution of {col}", dimension=col, measure=col, aggregation="count")

        elif chart_type == "donut":
            dim = detected_col if detected_col and detected_col in self._dimensions else self._most_relevant_dimension()
            measure = self._most_relevant_measure()
            if not dim or not measure:
                return None
            if dim and dim in self.col_stats:
                n_unique = self.col_stats[dim].n_unique
                if n_unique and n_unique > 8:
                    return self._make_spec("bar", title=f"{measure} by {dim}", dimension=dim, measure=measure, aggregation=agg)
            return self._make_spec("donut", title=f"{dim} Composition", dimension=dim, measure=measure, aggregation=agg)

        elif chart_type == "scatter":
            measures_in_text = [c for c in cols_in_text if c in self._measures]
            if len(measures_in_text) >= 2:
                return self._make_spec("scatter", title=f"{measures_in_text[0]} vs {measures_in_text[1]}", dimension=measures_in_text[0], measure=measures_in_text[1])
            elif detected_col and len(self._measures) >= 2:
                other = next((m for m in self._measures if m != detected_col), None)
                if other:
                    return self._make_spec("scatter", title=f"{detected_col} vs {other}", dimension=detected_col, measure=other)
            return None

        elif chart_type == "area":
            date_col = self._dates[0] if self._dates else None
            measure = detected_col if detected_col and detected_col in self._measures else self._most_relevant_measure()
            if not date_col or not measure:
                return None
            return self._make_spec("area", title=f"Cumulative {measure}",
                                   dimension=date_col, measure=measure, aggregation=agg)

        elif chart_type == "heatmap":
            if len(self._dimensions) >= 2:
                return self._make_spec("heatmap",
                                       title=f"{self._dimensions[0]} × {self._dimensions[1]} Heatmap",
                                       dimension=self._dimensions[0],
                                       measure=self._measures[0] if self._measures else None,
                                       dimension2=self._dimensions[1])
            return None

        return None

    # ── Auto-plan fallback ────────────────────────────────────────────────────

    def _auto_plan_for_column(self, col: str) -> List[VisualSpec]:
        """
        Generate default charts for a specific column when no specific intent matched.
        """
        specs = []
        if col in self._measures:
            if self._dates:
                specs.append(self._make_spec("line", title=f"{col} over Time", dimension=self._dates[0], measure=col))
            if self._dimensions:
                specs.append(self._make_spec("bar", title=f"{col} by {self._dimensions[0]}", dimension=self._dimensions[0], measure=col))
            specs.append(self._make_spec("histogram", title=f"Distribution of {col}", dimension=col, measure=col, aggregation="count"))
        elif col in self._dimensions:
            specs.append(self._make_spec("bar", title=f"{col} Distribution", dimension=col, measure=None, aggregation="count"))
            if self._measures:
                specs.append(self._make_spec("bar", title=f"{self._measures[0]} by {col}", dimension=col, measure=self._measures[0]))
        elif col in self._dates:
            if self._measures:
                specs.append(self._make_spec("line", title=f"{self._measures[0]} over Time", dimension=col, measure=self._measures[0]))
        
        # Deduplicate and return top 2
        return specs[:2]

    def _auto_plan(self) -> List[VisualSpec]:
        """
        Generates a sensible default set of visuals purely from the data schema.
        This is the Phase 4 DashboardPlanner logic embedded here for simplicity.
        """
        specs = []
        priority = 1

        # 1. Time-series for each measure + primary date
        if self._dates and self._measures:
            date_col = self._dates[0]
            for m in self._measures[:3]:
                specs.append(self._make_spec("line", f"{m} over Time",
                                             dimension=date_col, measure=m,
                                             aggregation="sum", priority=priority))
                priority += 1

        # 2. Bar charts: top dimensions vs top measures
        if self._dimensions and self._measures:
            for dim in self._dimensions[:3]:
                top_n = None
                if dim in self.col_stats and self.col_stats[dim].n_unique:
                    top_n = 10 if self.col_stats[dim].n_unique > 10 else None
                specs.append(self._make_spec("bar",
                                             f"{self._measures[0]} by {dim}",
                                             dimension=dim, measure=self._measures[0],
                                             aggregation="sum", top_n=top_n, priority=priority))
                priority += 1

        # 3. Distribution histograms for numeric cols
        for m in self._measures[:2]:
            specs.append(self._make_spec("histogram", f"Distribution of {m}",
                                         dimension=m, measure=m, aggregation="count",
                                         priority=priority))
            priority += 1

        # 4. Scatter for correlated numeric pairs
        if len(self._measures) >= 2:
            specs.append(self._make_spec("scatter",
                                         f"{self._measures[0]} vs {self._measures[1]}",
                                         dimension=self._measures[0], measure=self._measures[1],
                                         priority=priority))
            priority += 1

        # 5. Donut for low-cardinality dimensions
        for dim in self._dimensions[:2]:
            n_unique = self.col_stats.get(dim, None)
            if n_unique and hasattr(n_unique, 'n_unique') and n_unique.n_unique and n_unique.n_unique <= 8:
                specs.append(self._make_spec("donut", f"{dim} Breakdown",
                                             dimension=dim, measure=self._measures[0] if self._measures else None,
                                             aggregation="sum", priority=priority))
                priority += 1

        return specs

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _make_spec(self, chart_type: str, title: str, dimension: Optional[str],
                   measure: Optional[str], aggregation: str = "sum",
                   top_n: Optional[int] = None, dimension2: Optional[str] = None,
                   priority: int = 5) -> VisualSpec:
        dim_clean = re.sub(r'[^a-zA-Z0-9]', '', dimension or '')
        meas_clean = re.sub(r'[^a-zA-Z0-9]', '', measure or '')
        spec_id = f"{chart_type}_{dim_clean}_{meas_clean}_{uuid.uuid4().hex[:6]}"
        # Populate data
        data = self._build_data(chart_type, dimension, measure, aggregation, top_n)
        return VisualSpec(
            id=spec_id,
            chart_type=chart_type,
            title=title,
            dimension=dimension,
            dimension2=dimension2,
            measure=measure,
            aggregation=aggregation,
            top_n=top_n,
            data=data,
            priority=priority,
            reason="Description-driven plan",
        )

    def _build_data(self, chart_type: str, dimension: Optional[str],
                    measure: Optional[str], aggregation: str,
                    top_n: Optional[int]) -> dict:
        """Compute actual chart data from the dataframe."""
        data: dict = {}
        try:
            df = self.df
            if chart_type in ("line", "bar", "area", "donut") and dimension:
                if measure and measure in df.columns and dimension in df.columns:
                    agg_fn = {"sum": "sum", "mean": "mean", "count": "count",
                              "max": "max", "min": "min", "median": "median"}.get(aggregation, "sum")
                    grouped = df.groupby(dimension)[measure].agg(agg_fn).reset_index()
                    grouped = grouped.dropna()
                    if top_n:
                        grouped = grouped.nlargest(top_n, measure)
                    data["labels"] = grouped[dimension].astype(str).tolist()
                    data["values"] = grouped[measure].round(2).tolist()
                elif dimension in df.columns:
                    counts = df[dimension].value_counts()
                    if top_n:
                        counts = counts.head(top_n)
                    data["labels"] = counts.index.astype(str).tolist()
                    data["values"] = counts.values.tolist()

            elif chart_type == "histogram" and dimension and dimension in df.columns:
                series = df[dimension].dropna()
                if pd.api.types.is_numeric_dtype(series):
                    counts, edges = pd.cut(series, bins=20, retbins=True)
                    freq = counts.value_counts().sort_index()
                    data["labels"] = [f"{e:.1f}" for e in edges[:-1]]
                    data["values"] = freq.values.tolist()

            elif chart_type == "scatter" and dimension and measure:
                if dimension in df.columns and measure in df.columns:
                    sample = df[[dimension, measure]].dropna().head(500)
                    data["x"] = sample[dimension].round(3).tolist()
                    data["y"] = sample[measure].round(3).tolist()

        except Exception as e:
            logger.warning("Could not compute chart data for %s(%s, %s): %s",
                           chart_type, dimension, measure, e)
        return data

    def _detect_aggregation(self, text: str) -> str:
        t = text.lower()
        for kw, agg in _AGG_MAP.items():
            if kw in t:
                return agg
        return "sum"

    def _detect_top_n(self, text: str) -> Optional[int]:
        m = re.search(r"\btop[\s-](\d+)\b", text, re.I)
        if m:
            return int(m.group(1))
        return None

    def _find_columns_in_text(self, text: str) -> List[str]:
        found = []
        t = text.lower()
        # 1. Exact substring matches
        for lower_col, orig_col in self._col_lower.items():
            if lower_col in t and orig_col not in found:
                found.append(orig_col)
        
        # 2. Fuzzy matches for typos
        import difflib
        words = re.findall(r'\b\w+\b', t)
        for i in range(len(words)):
            # Unigram match
            matches = difflib.get_close_matches(words[i], self._col_lower.keys(), n=1, cutoff=0.75)
            if matches:
                col = self._col_lower[matches[0]]
                if col not in found: found.append(col)
            
            # Bigram match (for two-word columns like 'annual income')
            if i < len(words) - 1:
                bigram = f"{words[i]} {words[i+1]}"
                matches2 = difflib.get_close_matches(bigram, self._col_lower.keys(), n=1, cutoff=0.8)
                if matches2:
                    col = self._col_lower[matches2[0]]
                    if col not in found: found.append(col)
                    
        return found

    def _resolve_column(self, name: str) -> Optional[str]:
        if not name:
            return None
        norm = name.lower().strip()
        if norm in self._col_lower:
            return self._col_lower[norm]
        # Substring match
        for lower_col, orig_col in self._col_lower.items():
            if norm in lower_col or lower_col in norm:
                return orig_col
        # Fuzzy match for typos (e.g. "gendre" -> "gender")
        import difflib
        matches = difflib.get_close_matches(norm, self._col_lower.keys(), n=1, cutoff=0.7)
        if matches:
            return self._col_lower[matches[0]]
        return None

    def _most_relevant_measure(self) -> Optional[str]:
        if not self._measures:
            return None
        # Pick the measure with highest relevance score if available
        return self._measures[0]

    def _most_relevant_dimension(self) -> Optional[str]:
        if not self._dimensions:
            return None
        return self._dimensions[0]

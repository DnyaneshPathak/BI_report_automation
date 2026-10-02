"""
dashboard/change_interpreter.py
---------------------------------
Interprets plain-text user feedback and adjusts chart / KPI configuration.

This is a HEURISTIC rule engine — no LLM, no cloud.
It parses keywords and phrases to modify the ChartSelector's priority list.

Supported instructions (examples):
  - "add a pie chart for Category"
  - "remove scatter plots"
  - "focus on Revenue trends"
  - "show top 5 categories"
  - "hide Region"
  - "more bar charts"
  - "show distribution of Sales"
  - "add line chart for Date vs Sales"
  - "remove histogram"
  - "prioritize Profit"
  - "show correlation between Sales and Cost"
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from dashboard.chart_selector import ChartSpec
from preprocessing.datatype_detector import ColumnProfile

logger = logging.getLogger(__name__)


@dataclass
class InterpretedChange:
    """Result of interpreting user feedback text."""
    summary: str                            # human-readable summary
    add_chart_types: List[str] = field(default_factory=list)    # force-add these chart types
    remove_chart_types: Set[str] = field(default_factory=set)   # remove these chart types
    focus_columns: List[str] = field(default_factory=list)      # boost relevance for these cols
    hide_columns: Set[str] = field(default_factory=set)         # exclude these cols
    top_n: Optional[int] = None                                 # limit categories to top N
    force_charts: List[ChartSpec] = field(default_factory=list) # fully built specs to inject
    page_remap: Dict[str, int] = field(default_factory=dict)    # move chart type to page N


# Chart type synonyms
CHART_SYNONYMS: Dict[str, str] = {
    "pie": "donut",
    "donut": "donut",
    "doughnut": "donut",
    "bar": "bar",
    "column": "bar",
    "horizontal bar": "bar",
    "line": "line",
    "trend": "line",
    "time series": "line",
    "scatter": "scatter",
    "bubble": "scatter",
    "scatter plot": "scatter",
    "histogram": "histogram",
    "distribution": "histogram",
    "treemap": "treemap",
    "tree map": "treemap",
    "stacked": "stacked_bar",
    "stacked bar": "stacked_bar",
    "multi line": "multi_line",
    "multiline": "multi_line",
}


class ChangeInterpreter:

    def __init__(
        self,
        profiles: Dict[str, ColumnProfile],
        existing_specs: List[ChartSpec],
    ):
        self.profiles = profiles
        self.existing_specs = existing_specs
        self._col_names_lower: Dict[str, str] = {
            c.lower(): c for c in profiles.keys()
        }

    def interpret(self, text: str) -> InterpretedChange:
        """Parse free-text feedback into a structured InterpretedChange."""
        if not text or not text.strip():
            return InterpretedChange(summary="No changes specified.")

        text_l = text.lower().strip()
        change = InterpretedChange(summary="")
        summaries = []

        # ── Remove / hide instructions ────────────────────────────────────────
        # "remove scatter", "hide histogram", "no pie charts", "delete bar"
        remove_pats = [
            r"\b(?:remove|hide|delete|exclude|no|without)\s+(?:the\s+)?(?:all\s+)?([a-z\s]+?)\s*(?:chart|plot|graph|charts|plots)?\b",
        ]
        for pat in remove_pats:
            for m in re.finditer(pat, text_l):
                raw = m.group(1).strip()
                ct = self._resolve_chart_type(raw)
                if ct:
                    change.remove_chart_types.add(ct)
                    summaries.append(f"Remove {ct} charts")
                else:
                    col = self._resolve_column(raw)
                    if col:
                        change.hide_columns.add(col)
                        summaries.append(f"Hide column '{col}'")

        # ── Add chart instructions ────────────────────────────────────────────
        # "add a bar chart", "add pie chart for Category"
        add_pats = [
            r"\badd\s+(?:a\s+|an\s+)?([a-z\s]+?)\s*(?:chart|plot|graph)(?:\s+for\s+(.+?))?(?:\s+of\s+(.+?))?(?:\s+vs\.?\s+(.+?))?(?:\s*$|\.|\,)",
            r"\binclude\s+(?:a\s+|an\s+)?([a-z\s]+?)\s*(?:chart|plot|graph)(?:\s+for\s+(.+?))?(?:\s*$|\.|\,)",
            r"\bshow\s+(?:a\s+|an\s+)?([a-z\s]+?)\s*(?:chart|plot|graph)(?:\s+for\s+(.+?))?(?:\s*$|\.|\,)",
        ]
        for pat in add_pats:
            for m in re.finditer(pat, text_l):
                raw_type  = m.group(1).strip()
                raw_col1  = (m.group(2) or "").strip() if m.lastindex >= 2 else ""
                raw_col2  = (m.group(4) or "").strip() if m.lastindex >= 4 else ""
                ct = self._resolve_chart_type(raw_type)
                if ct:
                    col1 = self._resolve_column(raw_col1) if raw_col1 else None
                    col2 = self._resolve_column(raw_col2) if raw_col2 else None
                    spec = self._build_spec(ct, col1, col2)
                    if spec:
                        change.force_charts.append(spec)
                        summaries.append(f"Add {ct} chart" + (f" for '{col1}'" if col1 else ""))
                    else:
                        change.add_chart_types.append(ct)
                        summaries.append(f"Add more {ct} charts")

        # ── "More X charts" ────────────────────────────────────────────────────
        more_pats = [
            r"\bmore\s+([a-z\s]+?)\s*(?:charts?|plots?|graphs?)?\b",
        ]
        for pat in more_pats:
            for m in re.finditer(pat, text_l):
                raw = m.group(1).strip()
                ct  = self._resolve_chart_type(raw)
                if ct and ct not in change.add_chart_types:
                    change.add_chart_types.append(ct)
                    summaries.append(f"Prioritise {ct} charts")

        # ── Focus / prioritise columns ────────────────────────────────────────
        # "focus on Revenue", "prioritize Profit", "emphasize Sales"
        focus_pats = [
            r"\b(?:focus|emphasize|emphasise|prioritize|prioritise|highlight)\s+(?:on\s+)?(.+?)(?:\s*$|\.|\,)",
        ]
        for pat in focus_pats:
            for m in re.finditer(pat, text_l):
                raw = m.group(1).strip()
                col = self._resolve_column(raw)
                if col and col not in change.focus_columns:
                    change.focus_columns.append(col)
                    summaries.append(f"Focus on '{col}'")

        # ── "Show distribution of X" ────────────────────────────────────────
        dist_pats = [
            r"\b(?:show|display)\s+(?:the\s+)?distribution\s+of\s+(.+?)(?:\s*$|\.|\,)",
            r"\bhistogram\s+(?:of|for)\s+(.+?)(?:\s*$|\.|\,)",
        ]
        for pat in dist_pats:
            for m in re.finditer(pat, text_l):
                col = self._resolve_column(m.group(1).strip())
                if col:
                    spec = self._build_spec("histogram", col, None)
                    if spec:
                        change.force_charts.append(spec)
                        summaries.append(f"Distribution of '{col}'")

        # ── "Show correlation between A and B" ────────────────────────────────
        corr_pats = [
            r"\b(?:correlation|relationship)\s+between\s+(.+?)\s+and\s+(.+?)(?:\s*$|\.|\,)",
        ]
        for pat in corr_pats:
            for m in re.finditer(pat, text_l):
                col1 = self._resolve_column(m.group(1).strip())
                col2 = self._resolve_column(m.group(2).strip())
                if col1 and col2:
                    spec = self._build_spec("scatter", col1, col2)
                    if spec:
                        change.force_charts.append(spec)
                        summaries.append(f"Scatter: '{col1}' vs '{col2}'")

        # ── "Show top N" ───────────────────────────────────────────────────────
        top_n_pat = r"\btop\s+(\d+)\b"
        for m in re.finditer(top_n_pat, text_l):
            change.top_n = int(m.group(1))
            summaries.append(f"Limit to top {change.top_n}")

        # ── "Focus on X trends / line chart for X" ────────────────────────────
        trend_pats = [
            r"\b(?:trend|trends|over time|time series)\s+(?:of|for)?\s+(.+?)(?:\s*$|\.|\,)",
            r"\b(?:line\s+chart|line\s+graph)\s+(?:of|for)?\s+(.+?)(?:\s*$|\.|\,)",
        ]
        for pat in trend_pats:
            for m in re.finditer(pat, text_l):
                col = self._resolve_column(m.group(1).strip())
                if col:
                    # Find a date column
                    date_col = next(
                        (c for c, p in self.profiles.items() if p.analytical_type == "datetime"),
                        None
                    )
                    spec = self._build_spec("line", date_col or col, col if date_col else None)
                    if spec:
                        change.force_charts.append(spec)
                        summaries.append(f"Trend line for '{col}'")

        # Build summary
        if summaries:
            change.summary = "; ".join(summaries)
        else:
            change.summary = "Instructions noted but no specific changes identified. Regenerating with default variation."
            logger.info("Change interpreter found no specific rules for: %s", text)

        logger.info("Interpreted changes: %s", change.summary)
        return change

    # ── Apply changes to existing specs ──────────────────────────────────────

    def apply(self, change: InterpretedChange, existing_specs: List[ChartSpec]) -> List[ChartSpec]:
        """Apply interpreted changes to produce a new spec list."""
        from dashboard.chart_selector import ChartSpec

        result = list(existing_specs)

        # Remove excluded chart types
        if change.remove_chart_types:
            result = [s for s in result if s.chart_type not in change.remove_chart_types]

        # Remove hidden columns
        if change.hide_columns:
            result = [
                s for s in result
                if s.x_column not in change.hide_columns and s.y_column not in change.hide_columns
            ]

        # Inject force-built specs (at page 1 front)
        for spec in change.force_charts:
            # Avoid duplicating if same chart_id already exists
            if not any(s.chart_id == spec.chart_id for s in result):
                result.insert(0, spec)

        # Promote focus_columns: move specs featuring focus columns to page 1
        for col in change.focus_columns:
            for spec in result:
                if spec.x_column == col or spec.y_column == col:
                    spec.page = 1
                    spec.priority = max(spec.priority + 20, 95)

        # Add preferred chart types from under-represented types
        if change.add_chart_types:
            existing_types = {s.chart_type for s in result}
            for ct in change.add_chart_types:
                if ct not in existing_types:
                    # Try to find a suitable spec from original pool
                    col = self._best_col_for_type(ct)
                    if col:
                        spec = self._build_spec(ct, col, None, page=2)
                        if spec:
                            result.append(spec)

        # Top N: limit labels in categorical charts
        if change.top_n:
            for spec in result:
                if spec.chart_type in ("bar", "donut", "treemap"):
                    if "labels" in spec.data and len(spec.data["labels"]) > change.top_n:
                        spec.data["labels"] = spec.data["labels"][: change.top_n]
                        spec.data["values"] = spec.data["values"][: change.top_n]

        # Re-sort by priority descending
        result.sort(key=lambda s: s.priority, reverse=True)

        # Re-assign pages (max 7 per page)
        page_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for spec in result:
            p = spec.page if spec.page in page_counts else 1
            if page_counts[p] >= 7:
                for np in range(1, 5):
                    if page_counts[np] < 7:
                        p = np
                        break
            spec.page = p
            page_counts[p] += 1

        return result

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _resolve_chart_type(self, raw: str) -> Optional[str]:
        raw = raw.strip().lower()
        for key, value in CHART_SYNONYMS.items():
            if key in raw:
                return value
        return None

    def _resolve_column(self, raw: str) -> Optional[str]:
        if not raw:
            return None
        raw_l = raw.strip().lower()
        # Exact match
        if raw_l in self._col_names_lower:
            return self._col_names_lower[raw_l]
        # Partial match
        for col_l, col in self._col_names_lower.items():
            if raw_l in col_l or col_l in raw_l:
                return col
        return None

    def _build_spec(self, chart_type: str, x_col: Optional[str], y_col: Optional[str], page: int = 1) -> Optional[ChartSpec]:
        """Build a minimal ChartSpec from column names."""
        from dashboard.chart_selector import ChartSpec
        import pandas as pd

        if not x_col and not y_col:
            return None

        # Defaults
        x = x_col or y_col
        y = y_col or x_col
        title_map = {
            "bar": f"{y} by {x}",
            "line": f"{y} over {x}",
            "scatter": f"{x} vs {y}",
            "donut": f"{x} Distribution",
            "histogram": f"Distribution of {x}",
            "treemap": f"{x} Breakdown",
            "stacked_bar": f"{y} by {x}",
            "multi_line": f"{y} Trends",
        }
        title = title_map.get(chart_type, f"{chart_type.title()}: {x}")
        chart_id = f"user_{chart_type}_{(x or '').replace(' ', '_')}_{(y or '').replace(' ', '_')}"

        return ChartSpec(
            chart_id   = chart_id,
            chart_type = chart_type,
            title      = title,
            x_column   = x or "",
            y_column   = y or "",
            page       = page,
            priority   = 99,
            data       = {},
        )

    def _best_col_for_type(self, chart_type: str) -> Optional[str]:
        """Pick the most suitable column for a given chart type."""
        numeric_cols = [
            c for c, p in self.profiles.items()
            if p.analytical_type in ("continuous", "discrete_numeric") and p.include_in_analysis
        ]
        cat_cols = [
            c for c, p in self.profiles.items()
            if p.analytical_type in ("categorical_nominal", "categorical_ordinal")
        ]
        date_cols = [
            c for c, p in self.profiles.items()
            if p.analytical_type == "datetime"
        ]
        if chart_type in ("bar", "donut", "treemap") and cat_cols:
            return cat_cols[0]
        if chart_type in ("line", "multi_line") and date_cols:
            return date_cols[0]
        if chart_type in ("histogram", "scatter") and numeric_cols:
            return numeric_cols[0]
        return numeric_cols[0] if numeric_cols else None

"""
src/bi_automation/intent/parser.py
---------------------------------
Interprets plain-text user feedback and adjusts chart / KPI configuration.

This is a deterministic, regex-free grammar parser.
It tokenizes input and scans for known command sequences to modify the ChartSelector's priority list.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from bi_automation.powerbi.models import ChartSpec
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
        """Parse free-text feedback deterministically."""
        if not text or not text.strip():
            return InterpretedChange(summary="No changes specified.")

        change = InterpretedChange(summary="")
        summaries = []

        # Tokenize (simple split by spaces and punctuation)
        clean_text = text.lower().replace(",", " ").replace(".", " ").replace("!", " ")
        tokens = [t for t in clean_text.split() if t]

        i = 0
        current_context_col = None
        while i < len(tokens):
            tok = tokens[i]
            
            # Try to opportunistically update context column
            for j in range(len(tokens), i, -1):
                col = self._resolve_column(" ".join(tokens[i:j]))
                if col:
                    current_context_col = col
                    break

            # Remove/Hide
            if tok in ("remove", "hide", "delete", "exclude", "no"):
                i += 1
                if i < len(tokens) and tokens[i] == "the": i += 1
                if i < len(tokens) and tokens[i] == "all": i += 1
                
                # Match chart type or column
                found = False
                for j in range(len(tokens), i, -1):
                    phrase = " ".join(tokens[i:j])
                    ct = self._resolve_chart_type(phrase)
                    if ct:
                        change.remove_chart_types.add(ct)
                        summaries.append(f"Remove {ct} charts")
                        i = j - 1
                        found = True
                        break
                    col = self._resolve_column(phrase)
                    if col:
                        change.hide_columns.add(col)
                        summaries.append(f"Hide column '{col}'")
                        i = j - 1
                        found = True
                        current_context_col = col
                        break
                if not found:
                    pass

            # Focus/Prioritize
            elif tok in ("focus", "emphasize", "prioritize", "highlight"):
                i += 1
                if i < len(tokens) and tokens[i] == "on": i += 1
                
                for j in range(len(tokens), i, -1):
                    phrase = " ".join(tokens[i:j])
                    col = self._resolve_column(phrase)
                    if col:
                        if col not in change.focus_columns:
                            change.focus_columns.append(col)
                            summaries.append(f"Focus on '{col}'")
                        i = j - 1
                        current_context_col = col
                        break

            # Distribution / Histogram
            elif tok == "distribution" or tok == "histogram":
                if tok == "distribution":
                    i += 1
                    if i < len(tokens) and tokens[i] in ("of", "for"): i += 1
                else:
                    i += 1
                    if i < len(tokens) and tokens[i] in ("of", "for"): i += 1
                    
                found_col = None
                for j in range(len(tokens), i, -1):
                    phrase = " ".join(tokens[i:j])
                    col = self._resolve_column(phrase)
                    if col:
                        found_col = col
                        i = j - 1
                        current_context_col = col
                        break
                
                if not found_col and current_context_col:
                    found_col = current_context_col
                
                if found_col:
                    spec = self._build_spec("histogram", found_col, None)
                    if spec:
                        change.force_charts.append(spec)
                        summaries.append(f"Distribution of '{found_col}'")
            
            # Correlation
            elif tok == "correlation" or tok == "relationship":
                i += 1
                if i < len(tokens) and tokens[i] == "between": i += 1
                
                # We need to find "A and B"
                # Scan ahead for "and"
                and_idx = -1
                for j in range(i, len(tokens)):
                    if tokens[j] == "and":
                        and_idx = j
                        break
                
                if and_idx != -1:
                    col1_phrase = " ".join(tokens[i:and_idx])
                    col2_phrase = " ".join(tokens[and_idx+1:])
                    # Try to resolve col1 and col2
                    col1 = self._resolve_column(col1_phrase)
                    
                    if col1:
                        # Find col2 progressively
                        for k in range(len(tokens), and_idx, -1):
                            phrase = " ".join(tokens[and_idx+1:k])
                            col2 = self._resolve_column(phrase)
                            if col2:
                                spec = self._build_spec("scatter", col1, col2)
                                if spec:
                                    change.force_charts.append(spec)
                                    summaries.append(f"Scatter: '{col1}' vs '{col2}'")
                                i = k - 1
                                break

            # Top N
            elif tok == "top":
                i += 1
                if i < len(tokens) and tokens[i].isdigit():
                    change.top_n = int(tokens[i])
                    summaries.append(f"Limit to top {change.top_n}")
            
            # Trend
            elif tok in ("trend", "trends"):
                i += 1
                if i < len(tokens) and tokens[i] in ("of", "for"): i += 1
                
                found_col = None
                for j in range(len(tokens), i, -1):
                    phrase = " ".join(tokens[i:j])
                    col = self._resolve_column(phrase)
                    if col:
                        found_col = col
                        i = j - 1
                        current_context_col = col
                        break
                
                if not found_col and current_context_col:
                    found_col = current_context_col
                
                if found_col:
                    date_col = next((c for c, p in self.profiles.items() if p.analytical_type == "datetime"), None)
                    spec = self._build_spec("line", date_col or found_col, found_col if date_col else None)
                    if spec:
                        change.force_charts.append(spec)
                        summaries.append(f"Trend line for '{found_col}'")
            
            # Add / Show / Include
            elif tok in ("add", "show", "include"):
                i += 1
                if i < len(tokens) and tokens[i] in ("a", "an"): i += 1
                
                # Scan for chart type
                ct = None
                ct_end = i
                for j in range(len(tokens), i, -1):
                    phrase = " ".join(tokens[i:j])
                    ct = self._resolve_chart_type(phrase)
                    if ct:
                        ct_end = j
                        break
                
                if ct:
                    i = ct_end
                    if i < len(tokens) and tokens[i] in ("chart", "plot", "graph"): i += 1
                    
                    found_col = None
                    # See if "for X" or "of X" is next
                    if i < len(tokens) and tokens[i] in ("for", "of"):
                        i += 1
                        for j in range(len(tokens), i, -1):
                            phrase = " ".join(tokens[i:j])
                            col = self._resolve_column(phrase)
                            if col:
                                found_col = col
                                i = j - 1
                                current_context_col = col
                                break
                    
                    if not found_col and current_context_col:
                        found_col = current_context_col
                        
                    if found_col:
                        spec = self._build_spec(ct, found_col, None)
                        if spec:
                            change.force_charts.append(spec)
                            summaries.append(f"Add {ct} chart for '{found_col}'")
                    else:
                        if ct not in change.add_chart_types:
                            change.add_chart_types.append(ct)
                            summaries.append(f"Add more {ct} charts")

            # More
            elif tok == "more":
                i += 1
                for j in range(len(tokens), i, -1):
                    phrase = " ".join(tokens[i:j])
                    ct = self._resolve_chart_type(phrase)
                    if ct:
                        if ct not in change.add_chart_types:
                            change.add_chart_types.append(ct)
                            summaries.append(f"Prioritise {ct} charts")
                        i = j - 1
                        break
                        
            i += 1

        if summaries:
            change.summary = "; ".join(summaries)
        else:
            change.summary = "Instructions noted but no specific changes identified. Regenerating with default variation."
            logger.info("Change interpreter found no specific rules.")

        logger.info("Interpreted changes: %s", change.summary)
        return change


    def apply(self, change: InterpretedChange, existing_specs: List[ChartSpec]) -> List[ChartSpec]:
        """Apply interpreted changes to produce a new spec list."""
        from bi_automation.powerbi.models import ChartSpec

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

        # Boost priority of focus columns
        if change.focus_columns:
            for s in result:
                if s.x_column in change.focus_columns or s.y_column in change.focus_columns:
                    s.priority = max(1, s.priority - 2)

        # If top_n is applied, maybe just store it on bar charts (for now just general logic)
        # We don't have a direct field for "limit" in ChartSpec yet, but we could add it.
        
        # Boost chart types requested
        if change.add_chart_types:
            for s in result:
                if s.chart_type in change.add_chart_types:
                    s.priority = max(1, s.priority - 1)

        result.sort(key=lambda s: s.priority)
        return result


    # ── Helpers ───────────────────────────────────────────────────────────────

    def _resolve_column(self, name: str) -> Optional[str]:
        """Fuzzy match column name from profiles."""
        if not name:
            return None
        norm = name.lower().strip()
        # Exact match
        if norm in self._col_names_lower:
            return self._col_names_lower[norm]
        
        # Substring match (e.g. "revenue" matching "Total Revenue")
        for lower_col, orig_col in self._col_names_lower.items():
            if norm in lower_col:
                return orig_col
        return None

    def _resolve_chart_type(self, text: str) -> Optional[str]:
        """Match phrase to a known chart type."""
        norm = text.lower().strip()
        for k, v in CHART_SYNONYMS.items():
            if k in norm:
                return v
        return None

    def _build_spec(self, chart_type: str, x_col: Optional[str], y_col: Optional[str], page: int = 1) -> Optional[ChartSpec]:
        """Build a minimal ChartSpec from column names."""
        import uuid
        from bi_automation.powerbi.models import ChartSpec
        
        if not x_col:
            return None
        
        y_col_safe = y_col or ""
        
        return ChartSpec(
            chart_id=f"{chart_type}_{x_col}_{y_col_safe}_{str(uuid.uuid4())[:6]}",
            chart_type=chart_type,
            title=f"Custom {chart_type.capitalize()} for {x_col}",
            x_column=x_col,
            y_column=y_col_safe,
            page=page,
            priority=1,
            reason="User requested change."
        )

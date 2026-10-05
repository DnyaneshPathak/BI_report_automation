"""
dashboard/dax_generator.py
---------------------------
Generates DAX measure definitions for the Power BI model.

Rules:
  - Only creates measures when underlying columns exist
  - Readable naming conventions
  - No measures for identifier columns
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List

from preprocessing.datatype_detector import ColumnProfile
from dashboard.kpi_detector import KPI

logger = logging.getLogger(__name__)


@dataclass
class DAXMeasure:
    name: str
    expression: str
    table: str
    category: str    # aggregate | ratio | time_intelligence | count


class DAXGenerator:

    def __init__(
        self,
        profiles: Dict[str, ColumnProfile],
        kpis: List[KPI],
        table_name: str = "DataTable",
    ):
        self.profiles   = profiles
        self.kpis       = kpis
        self.table_name = table_name

    def generate(self) -> List[DAXMeasure]:
        measures: List[DAXMeasure] = []
<<<<<<< HEAD
=======
        
        # Include KPI measures
        for k in self.kpis:
            if k.dax_measure:
                # Format: [Measure Name] = Expression
                parts = k.dax_measure.split("=", 1)
                if len(parts) == 2:
                    name = parts[0].strip().strip("[]")
                    expr = parts[1].strip()
                    measures.append(DAXMeasure(name=name, expression=expr, table=self.table_name, category="kpi"))

>>>>>>> master
        measures += self._aggregate_measures()
        measures += self._ratio_measures()
        measures += self._count_measures()
        measures += self._time_intelligence_measures()
        # Deduplicate by name
        seen = set()
        unique = []
        for m in measures:
            if m.name not in seen:
                seen.add(m.name)
                unique.append(m)
        return unique

    # ── Aggregate measures (SUM / AVERAGE) ────────────────────────────────────
    def _aggregate_measures(self) -> List[DAXMeasure]:
        results = []
        for col, profile in self.profiles.items():
            if profile.analytical_type not in ("continuous", "discrete_numeric"):
                continue
            if not profile.include_in_analysis:
                continue
            if profile.feature_role in ("Financial Measure", "Measure", "Target-Like Metric"):
                safe = self._safe(col)
                results.append(DAXMeasure(
                    name=f"Total {col}",
                    expression=f"SUM('{self.table_name}'[{col}])",
                    table=self.table_name,
                    category="aggregate",
                ))
                results.append(DAXMeasure(
                    name=f"Avg {col}",
                    expression=f"AVERAGE('{self.table_name}'[{col}])",
                    table=self.table_name,
                    category="aggregate",
                ))
            elif profile.feature_role == "Quantity":
                results.append(DAXMeasure(
                    name=f"Total {col}",
                    expression=f"SUM('{self.table_name}'[{col}])",
                    table=self.table_name,
                    category="aggregate",
                ))
        return results[:8]

    # ── Ratio measures ────────────────────────────────────────────────────────
    def _ratio_measures(self) -> List[DAXMeasure]:
        results = []
        numeric_measures = [
            col for col, p in self.profiles.items()
            if p.analytical_type in ("continuous", "discrete_numeric")
            and p.include_in_analysis
            and p.feature_role in ("Financial Measure", "Measure")
        ]
        # Profit margin if we have revenue + profit/cost
        rev_col  = next((c for c in numeric_measures if "revenue" in c.lower() or "sales" in c.lower()), None)
        prof_col = next((c for c in numeric_measures if "profit" in c.lower()), None)
        cost_col = next((c for c in numeric_measures if "cost" in c.lower()), None)

        if rev_col and prof_col:
            results.append(DAXMeasure(
                name="Profit Margin %",
                expression=(
                    f"DIVIDE(SUM('{self.table_name}'[{prof_col}]), "
                    f"SUM('{self.table_name}'[{rev_col}]), 0) * 100"
                ),
                table=self.table_name,
                category="ratio",
            ))
        if rev_col and cost_col:
            results.append(DAXMeasure(
                name="Gross Profit",
                expression=(
                    f"SUM('{self.table_name}'[{rev_col}]) - "
                    f"SUM('{self.table_name}'[{cost_col}])"
                ),
                table=self.table_name,
                category="ratio",
            ))
        return results

    # ── Count measures ────────────────────────────────────────────────────────
    def _count_measures(self) -> List[DAXMeasure]:
        results = [
            DAXMeasure(
                name="Total Records",
                expression=f"COUNTROWS('{self.table_name}')",
                table=self.table_name,
                category="count",
            )
        ]
        for col, profile in self.profiles.items():
            if profile.analytical_type == "identifier" and profile.feature_role == "Identifier":
                results.append(DAXMeasure(
                    name=f"Distinct {col} Count",
                    expression=f"DISTINCTCOUNT('{self.table_name}'[{col}])",
                    table=self.table_name,
                    category="count",
                ))
                break
        return results

    # ── Time intelligence measures ────────────────────────────────────────────
    def _time_intelligence_measures(self) -> List[DAXMeasure]:
        results = []
        date_cols = [
            col for col, p in self.profiles.items()
            if p.analytical_type == "datetime"
        ]
        numeric_measures = [
            col for col, p in self.profiles.items()
            if p.analytical_type in ("continuous", "discrete_numeric")
            and p.include_in_analysis
            and p.feature_role in ("Financial Measure", "Measure", "Quantity")
        ]
        if not date_cols or not numeric_measures:
            return results

        num_col  = numeric_measures[0]
        date_col = date_cols[0]

        results.append(DAXMeasure(
            name=f"YoY Growth % ({num_col})",
            expression=(
                f"VAR CurrentValue = SUM('{self.table_name}'[{num_col}])\n"
                f"VAR PrevYearValue = CALCULATE(SUM('{self.table_name}'[{num_col}]), SAMEPERIODLASTYEAR('DateTable'[Date]))\n"
                "RETURN DIVIDE(CurrentValue - PrevYearValue, ABS(PrevYearValue), BLANK()) * 100"
            ),
            table=self.table_name,
            category="time_intelligence",
        ))
        results.append(DAXMeasure(
            name=f"Running Total ({num_col})",
            expression=(
                f"CALCULATE(\n"
                f"  SUM('{self.table_name}'[{num_col}]),\n"
                f"  FILTER(\n"
                f"    ALL('DateTable'),\n"
                f"    'DateTable'[Date] <= MAX('DateTable'[Date])\n"
                f"  )\n)"
            ),
            table=self.table_name,
            category="time_intelligence",
        ))
        return results

    @staticmethod
    def _safe(col: str) -> str:
        return col.replace(" ", "_").replace("-", "_")

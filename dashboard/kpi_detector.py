"""
dashboard/kpi_detector.py
--------------------------
Automatically detects business KPIs from the dataset.

Only creates KPIs supported by the data.
Never invents unavailable metrics.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from preprocessing.datatype_detector import ColumnProfile
from analysis.profiler import ColumnStats

logger = logging.getLogger(__name__)

# ── KPI definition templates ──────────────────────────────────────────────────
@dataclass
class KPI:
    title: str
    value: float
    formatted_value: str
    dax_measure: str
    icon: str = "📊"
    description: str = ""
    secondary_value: Optional[float] = None
    secondary_label: Optional[str] = None
    unit: str = ""


_FINANCIAL_PATTERNS = re.compile(
    r"\b(revenue|sales|profit|income|amount|value|cost|price|fee|spend|budget|earning)\b", re.I
)
_QUANTITY_PATTERNS = re.compile(
    r"\b(quantity|qty|units?|volume|count|orders?|bookings?|tickets?|transactions?)\b", re.I
)
_RATE_PATTERNS = re.compile(
    r"\b(rate|ratio|pct|percent|cancell|churn|conversion|margin)\b", re.I
)
_CUSTOMER_PATTERNS = re.compile(r"\b(customer|client|user|member|passenger|guest)\b", re.I)


class KPIDetector:

    def __init__(
        self,
        df: pd.DataFrame,
        profiles: Dict[str, ColumnProfile],
        col_stats: Dict[str, ColumnStats],
    ):
        self.df        = df
        self.profiles  = profiles
        self.col_stats = col_stats

    def detect(self) -> List[KPI]:
        kpis: List[KPI] = []

        kpis += self._detect_totals()
        kpis += self._detect_averages()
        kpis += self._detect_counts()
        kpis += self._detect_rates()

        # Deduplicate by title, cap at 6
        seen = set()
        unique = []
        for k in kpis:
            if k.title not in seen:
                seen.add(k.title)
                unique.append(k)
        return unique[:6]

    # ── Totals ────────────────────────────────────────────────────────────────
    def _detect_totals(self) -> List[KPI]:
        results = []
        for col, profile in self.profiles.items():
            if col not in self.df.columns:
                continue
            if not (profile.include_in_analysis and
                    profile.analytical_type in ("continuous", "discrete_numeric")):
                continue
            if not _FINANCIAL_PATTERNS.search(col) and not _QUANTITY_PATTERNS.search(col):
                continue
            series = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(series) == 0:
                continue
            total = float(series.sum())
            label = self._friendly_label(col, "Total")
            icon  = "💰" if _FINANCIAL_PATTERNS.search(col) else "📦"
            results.append(KPI(
                title=label,
                value=total,
                formatted_value=self._format_number(total),
                dax_measure=f"[Total {col}] = SUM('{col}')",
                icon=icon,
                description=f"Sum of all {col} values.",
            ))
        return results[:3]

    # ── Averages ──────────────────────────────────────────────────────────────
    def _detect_averages(self) -> List[KPI]:
        results = []
        for col, profile in self.profiles.items():
            if col not in self.df.columns:
                continue
            if not (profile.include_in_analysis and
                    profile.analytical_type in ("continuous", "discrete_numeric")):
                continue
            if not _FINANCIAL_PATTERNS.search(col):
                continue
            series = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(series) == 0:
                continue
            avg = float(series.mean())
            label = self._friendly_label(col, "Avg")
            results.append(KPI(
                title=label,
                value=avg,
                formatted_value=self._format_number(avg),
                dax_measure=f"[Avg {col}] = AVERAGE('{col}')",
                icon="📈",
                description=f"Average {col} per record.",
            ))
        return results[:2]

    # ── Record counts ─────────────────────────────────────────────────────────
    def _detect_counts(self) -> List[KPI]:
        results = []
        n = len(self.df)

        # Total rows
        # Look for ID-like column to count distinct
        for col, profile in self.profiles.items():
            if profile.analytical_type == "identifier" and col in self.df.columns:
                distinct = int(self.df[col].nunique())
                label = self._friendly_label(col, "Total")
                results.append(KPI(
                    title=label,
                    value=distinct,
                    formatted_value=self._format_number(distinct),
                    dax_measure=f"[Distinct {col}] = DISTINCTCOUNT('{col}')",
                    icon="🔢",
                    description=f"Total distinct {col}.",
                ))
                break

        results.append(KPI(
            title="Total Records",
            value=n,
            formatted_value=self._format_number(n),
            dax_measure="[Total Records] = COUNTROWS(Table)",
            icon="📋",
            description="Total number of records in the dataset.",
        ))

        # Customer count
        for col in self.df.columns:
            if _CUSTOMER_PATTERNS.search(col):
                distinct = int(self.df[col].nunique())
                label = f"Total {col.title().replace('_', ' ')}"
                results.append(KPI(
                    title=label,
                    value=distinct,
                    formatted_value=self._format_number(distinct),
                    dax_measure=f"[Total {col}] = DISTINCTCOUNT('{col}')",
                    icon="👤",
                ))
                break

        return results[:2]

    # ── Rates ─────────────────────────────────────────────────────────────────
    def _detect_rates(self) -> List[KPI]:
        results = []
        for col, profile in self.profiles.items():
            if col not in self.df.columns or not profile.include_in_analysis:
                continue
            if _RATE_PATTERNS.search(col):
                if profile.analytical_type in ("continuous", "discrete_numeric"):
                    series = pd.to_numeric(self.df[col], errors="coerce").dropna()
                    if len(series) == 0:
                        continue
                    avg = float(series.mean())
                    results.append(KPI(
                        title=self._friendly_label(col, "Avg"),
                        value=avg,
                        formatted_value=f"{avg:.1f}%",
                        dax_measure=f"[Avg {col}] = AVERAGE('{col}')",
                        icon="📉",
                    ))
                elif profile.analytical_type in ("categorical_nominal", "binary"):
                    # Binary: compute % of "positive" value
                    valid = self.df[col].dropna().astype(str).str.strip().str.lower()
                    positive = {"cancelled", "cancel", "yes", "true", "1", "churn", "fail", "inactive"}
                    n_pos = valid.isin(positive).sum()
                    rate  = round(n_pos / max(len(valid), 1) * 100, 2)
                    results.append(KPI(
                        title=self._friendly_label(col, "Rate"),
                        value=rate,
                        formatted_value=f"{rate:.1f}%",
                        dax_measure=f"[{col} Rate] = ...",
                        icon="⚠️",
                    ))
        return results[:2]

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _friendly_label(col: str, prefix: str) -> str:
        human = col.replace("_", " ").replace("-", " ").title()
        return f"{prefix} {human}"

    @staticmethod
    def _format_number(value: float) -> str:
        if abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        elif abs(value) >= 1_000:
            return f"{value / 1_000:.1f}K"
        elif value != int(value):
            return f"{value:,.2f}"
        else:
            return f"{int(value):,}"

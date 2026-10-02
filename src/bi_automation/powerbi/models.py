from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ChartSpec:
    """
    Formal data model for a single visual/chart on the dashboard.
    """
    chart_id: str
    chart_type: str
    title: str
    x_column: str
    y_column: str
    group_column: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    page: int = 1         # 1=Overview, 2=Detail, 3=Trend, 4=Statistical
    priority: int = 5
    reason: str = ""


@dataclass
class DashboardSpec:
    """
    Formal data model representing the entire dashboard layout and context.
    """
    title: str
    pages: Dict[int, str] = field(default_factory=lambda: {
        1: "Executive Overview",
        2: "Detailed Analysis",
        3: "Trend Analysis",
        4: "Statistical Insights"
    })
    charts: List[ChartSpec] = field(default_factory=list)
    kpis: List[Any] = field(default_factory=list)
    dax_measures: List[Any] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    quality_summary: str = ""

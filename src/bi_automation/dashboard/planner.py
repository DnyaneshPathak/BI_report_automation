import logging
from typing import Dict, List

from bi_automation.models.domain import DashboardSpec, VisualSpec, PageSpec, KPIIntent
from preprocessing.datatype_detector import ColumnProfile
from analysis.profiler import ColumnStats
from analysis.bivariate import BivariatePair

logger = logging.getLogger(__name__)

class DashboardPlanner:
    """
    Phase 4: Dashboard Planner
    Creates a highly relevant DashboardSpec based on data statistics and schema.
    This acts as a fallback or foundational planner if NLP intent is missing or incomplete.
    """
    def __init__(
        self,
        profiles: Dict[str, ColumnProfile],
        stats: Dict[str, ColumnStats],
        bivariate: List[BivariatePair]
    ):
        self.profiles = profiles
        self.stats = stats
        self.bivariate = bivariate

    def plan(self, user_intent: str = "") -> DashboardSpec:
        spec = DashboardSpec(title="Auto-Generated Dashboard", description=user_intent)
        
        # 1. Identify primary metrics (continuous numeric)
        measures = [k for k, v in self.profiles.items() if v.analytical_type in ("continuous", "discrete_numeric")]
        
        # 2. Identify primary dimensions (categorical)
        dimensions = [k for k, v in self.profiles.items() if v.analytical_type in ("categorical_nominal", "categorical_ordinal")]
        
        # 3. Identify dates
        dates = [k for k, v in self.profiles.items() if v.analytical_type == "datetime"]
        
        # Add basic KPIs
        for m in measures[:4]:
            spec.kpis.append(KPIIntent(name=f"Total {m}", measure=m, aggregation="sum"))
            
        page = PageSpec(name="Overview")
        
        # Add a time-series if we have dates and measures
        if dates and measures:
            page.visuals.append(VisualSpec(
                id=f"ts_{dates[0]}_{measures[0]}",
                title=f"{measures[0]} over Time",
                chart_type="line",
                dimension=dates[0],
                measure=measures[0],
                aggregation="sum"
            ))
            
        # Add bar charts for categories
        if dimensions and measures:
            for i, dim in enumerate(dimensions[:2]):
                page.visuals.append(VisualSpec(
                    id=f"bar_{dim}_{measures[0]}",
                    title=f"{measures[0]} by {dim}",
                    chart_type="bar",
                    dimension=dim,
                    measure=measures[0],
                    aggregation="sum",
                    top_n=10
                ))
                
        # Add correlation scatter plots
        if len(measures) >= 2:
            page.visuals.append(VisualSpec(
                id=f"scatter_{measures[0]}_{measures[1]}",
                title=f"{measures[0]} vs {measures[1]}",
                chart_type="scatter",
                measure=measures[0],
                measure2=measures[1]
            ))

        spec.pages.append(page)
        return spec

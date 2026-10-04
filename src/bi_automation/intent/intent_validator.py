import logging
import re
from typing import Dict, Optional, Tuple, Any

from bi_automation.models.domain import DashboardIntent, DashboardSpec, VisualSpec, KPIIntent, PageSpec
from preprocessing.datatype_detector import ColumnProfile

logger = logging.getLogger(__name__)

class IntentValidator:
    """
    Stage 2 of Intent Processing.
    Deterministically validates AI-generated DashboardIntent against the actual dataset schemas.
    """
    def __init__(self, profiles: Dict[str, ColumnProfile]):
        self.profiles = profiles
        # Create a normalized index for fuzzy matching
        self._norm_index = {self._normalize(k): k for k in profiles.keys()}

    def _normalize(self, text: str) -> str:
        if not text: return ""
        return re.sub(r'[^a-z0-9]', '', str(text).lower())

    def resolve_column(self, col_name: str) -> Tuple[Optional[str], float]:
        """
        Attempts to semantically match a requested column name to an actual dataset column.
        Returns (actual_column_name, confidence).
        """
        if not col_name:
            return None, 0.0
            
        # 1. Exact match
        if col_name in self.profiles:
            return col_name, 1.0
            
        # 2. Normalized match
        norm = self._normalize(col_name)
        if norm in self._norm_index:
            return self._norm_index[norm], 0.9
            
        # 3. Substring/alias match (basic implementation)
        for act_norm, actual_col in self._norm_index.items():
            if norm in act_norm or act_norm in norm:
                return actual_col, 0.7
                
        return None, 0.0

    def validate(self, intent: DashboardIntent) -> DashboardSpec:
        """
        Takes raw AI intent and maps it safely to a DashboardSpec.
        Discards invalid fields/charts safely rather than generating broken Power BI output.
        """
        spec = DashboardSpec(title="AI Generated Dashboard", description="")
        
        # 1. Validate KPIs
        for k in intent.kpis:
            col, conf = self.resolve_column(k.measure)
            if col and self.profiles[col].analytical_type in ("continuous", "discrete_numeric"):
                valid_kpi = KPIIntent(
                    name=k.name or f"Total {col}",
                    measure=col,
                    aggregation=k.aggregation or "sum",
                    format=k.format
                )
                spec.kpis.append(valid_kpi)
            else:
                logger.warning(f"KPI rejected: Measure '{k.measure}' not found or not numeric.")

        # 2. Validate Visuals
        valid_visuals = []
        for v in intent.visuals:
            # Validate measure
            meas, meas_conf = self.resolve_column(v.measure)
            if v.measure and not meas:
                logger.warning(f"Visual '{v.title}' rejected: Measure '{v.measure}' not found.")
                continue
                
            # Validate dimension
            dim, dim_conf = self.resolve_column(v.dimension)
            if v.dimension and not dim:
                logger.warning(f"Visual '{v.title}' rejected: Dimension '{v.dimension}' not found.")
                continue

            v.measure = meas
            v.dimension = dim
            valid_visuals.append(v)

        # 3. Map to Pages
        # For simplicity in this implementation, push all valid visuals to page 1
        page1 = PageSpec(name="Executive Overview", visuals=valid_visuals)
        spec.pages.append(page1)

        return spec

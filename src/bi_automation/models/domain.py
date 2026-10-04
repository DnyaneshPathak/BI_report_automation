from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class KPIIntent:
    name: str
    measure: str
    aggregation: str
    format: Optional[str] = None
    target: Optional[float] = None
    value: Optional[float] = None  # Populated during evaluation
    formatted_value: Optional[str] = None

@dataclass
class VisualSpec:
    id: str
    title: str
    chart_type: str
    
    dimension: Optional[str] = None
    dimension2: Optional[str] = None
    
    measure: Optional[str] = None
    measure2: Optional[str] = None
    
    aggregation: Optional[str] = None
    legend: Optional[str] = None
    time_grain: Optional[str] = None
    
    sort_by: Optional[str] = None
    sort_direction: Optional[str] = None
    top_n: Optional[int] = None
    
    filters: List[Dict[str, Any]] = field(default_factory=list)
    page: Optional[str] = None
    
    tooltip_fields: List[str] = field(default_factory=list)
    drilldown_fields: List[str] = field(default_factory=list)
    drillthrough_page: Optional[str] = None
    conditional_formatting: Optional[Dict[str, Any]] = None

    # Backwards compatibility / selector fields
    group_column: Optional[str] = None
    priority: int = 5
    reason: str = ""

    # Holds data when previewing
    data: Optional[Dict[str, Any]] = None

@dataclass
class PageSpec:
    name: str
    visuals: List[VisualSpec] = field(default_factory=list)
    filters: List[Dict[str, Any]] = field(default_factory=list)
    slicers: List[Dict[str, Any]] = field(default_factory=list)
    layout: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DashboardSpec:
    title: str
    description: str
    kpis: List[KPIIntent] = field(default_factory=list)
    pages: List[PageSpec] = field(default_factory=list)
    global_filters: List[Dict[str, Any]] = field(default_factory=list)
    theme: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DashboardIntent:
    kpis: List[KPIIntent] = field(default_factory=list)
    visuals: List[VisualSpec] = field(default_factory=list)
    global_filters: List[Dict[str, Any]] = field(default_factory=list)
    pages: List[str] = field(default_factory=list)

@dataclass
class FeatureProfile:
    name: str
    dtype: str
    analytical_type: str  # identifier, numeric_measure, categorical_dimension, date, etc.
    missing_count: int = 0
    unique_count: int = 0
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    mean_val: Optional[float] = None
    median_val: Optional[float] = None

@dataclass
class DatasetProfile:
    features: Dict[str, FeatureProfile] = field(default_factory=dict)
    total_rows: int = 0
    total_columns: int = 0

@dataclass
class AnalysisConfig:
    selected_features: List[str] = field(default_factory=list)
    analysis_types: List[str] = field(default_factory=list)
    goal_description: str = ""

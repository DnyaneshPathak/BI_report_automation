from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class ChartDef:
    name: str
    display_name: str
    synonyms: List[str]
    data_shape: str # e.g. "1D_1M", "1D_NM", "2D_1M" (D=Dimension, M=Measure)
    required_roles: Dict[str, Any]
    ecs_builder: str # function/module name for ECharts
    pbi_visual_type: str # exact Power BI visual JSON type
    supports_dynamic: bool = True
    notes: str = ""

CHART_REGISTRY: Dict[str, ChartDef] = {
    # Basic Bars / Columns
    "bar": ChartDef(
        name="bar", display_name="Clustered Bar Chart",
        synonyms=["horizontal bar", "bar chart", "bars"],
        data_shape="1D_NM", required_roles={"x": "dimension", "y": "measure"},
        ecs_builder="build_bar", pbi_visual_type="clusteredBarChart"
    ),
    "column": ChartDef(
        name="column", display_name="Clustered Column Chart",
        synonyms=["vertical bar", "column chart", "columns"],
        data_shape="1D_NM", required_roles={"x": "dimension", "y": "measure"},
        ecs_builder="build_column", pbi_visual_type="clusteredColumnChart"
    ),
    "stacked_bar": ChartDef(
        name="stacked_bar", display_name="Stacked Bar Chart",
        synonyms=["stacked horizontal bar", "stacked bars"],
        data_shape="2D_NM", required_roles={"x": "dimension", "series": "dimension", "y": "measure"},
        ecs_builder="build_stacked_bar", pbi_visual_type="stackedBarChart"
    ),
    "stacked_column": ChartDef(
        name="stacked_column", display_name="Stacked Column Chart",
        synonyms=["stacked vertical bar", "stacked columns"],
        data_shape="2D_NM", required_roles={"x": "dimension", "series": "dimension", "y": "measure"},
        ecs_builder="build_stacked_column", pbi_visual_type="stackedColumnChart"
    ),
    "100_stacked_bar": ChartDef(
        name="100_stacked_bar", display_name="100% Stacked Bar Chart",
        synonyms=["percent stacked bar"],
        data_shape="2D_NM", required_roles={"x": "dimension", "series": "dimension", "y": "measure"},
        ecs_builder="build_100_stacked_bar", pbi_visual_type="hundredPercentStackedBarChart"
    ),
    "100_stacked_column": ChartDef(
        name="100_stacked_column", display_name="100% Stacked Column Chart",
        synonyms=["percent stacked column"],
        data_shape="2D_NM", required_roles={"x": "dimension", "series": "dimension", "y": "measure"},
        ecs_builder="build_100_stacked_column", pbi_visual_type="hundredPercentStackedColumnChart"
    ),
    
    # Lines & Areas
    "line": ChartDef(
        name="line", display_name="Line Chart",
        synonyms=["trend", "time series", "lines"],
        data_shape="1D_NM", required_roles={"x": ["date", "dimension"], "y": "measure"},
        ecs_builder="build_line", pbi_visual_type="lineChart"
    ),
    "area": ChartDef(
        name="area", display_name="Area Chart",
        synonyms=["filled line", "area graph"],
        data_shape="1D_NM", required_roles={"x": ["date", "dimension"], "y": "measure"},
        ecs_builder="build_area", pbi_visual_type="areaChart"
    ),
    "stacked_area": ChartDef(
        name="stacked_area", display_name="Stacked Area Chart",
        synonyms=["stacked filled line"],
        data_shape="2D_NM", required_roles={"x": ["date", "dimension"], "series": "dimension", "y": "measure"},
        ecs_builder="build_stacked_area", pbi_visual_type="stackedAreaChart"
    ),
    "combo": ChartDef(
        name="combo", display_name="Line and Clustered Column Chart",
        synonyms=["dual axis", "combination", "line and bar"],
        data_shape="1D_2M", required_roles={"x": "dimension", "y": "measure"},
        ecs_builder="build_combo", pbi_visual_type="lineClusteredColumnComboChart"
    ),
    
    # Parts of a whole
    "pie": ChartDef(
        name="pie", display_name="Pie Chart",
        synonyms=["slices", "pie graph"],
        data_shape="1D_1M", required_roles={"x": "dimension", "y": "measure"},
        ecs_builder="build_pie", pbi_visual_type="pieChart", supports_dynamic=False
    ),
    "donut": ChartDef(
        name="donut", display_name="Donut Chart",
        synonyms=["doughnut", "ring chart"],
        data_shape="1D_1M", required_roles={"x": "dimension", "y": "measure"},
        ecs_builder="build_donut", pbi_visual_type="donutChart", supports_dynamic=False
    ),
    "treemap": ChartDef(
        name="treemap", display_name="Treemap",
        synonyms=["tree map", "blocks"],
        data_shape="1D_1M", required_roles={"x": "dimension", "y": "measure"},
        ecs_builder="build_treemap", pbi_visual_type="treemap"
    ),
    
    # Statistical / Specific
    "scatter": ChartDef(
        name="scatter", display_name="Scatter Chart",
        synonyms=["plot", "points", "correlation"],
        data_shape="0D_2M", required_roles={"x": "measure", "y": "measure"},
        ecs_builder="build_scatter", pbi_visual_type="scatterChart"
    ),
    "bubble": ChartDef(
        name="bubble", display_name="Bubble Chart",
        synonyms=["scatter with size"],
        data_shape="0D_3M", required_roles={"x": "measure", "y": "measure", "size": "measure"},
        ecs_builder="build_scatter", pbi_visual_type="scatterChart"
    ),
    "waterfall": ChartDef(
        name="waterfall", display_name="Waterfall Chart",
        synonyms=["bridge chart", "buildup"],
        data_shape="1D_1M", required_roles={"x": "dimension", "y": "measure"},
        ecs_builder="build_waterfall", pbi_visual_type="waterfallChart"
    ),
    "funnel": ChartDef(
        name="funnel", display_name="Funnel Chart",
        synonyms=["conversion", "pipeline"],
        data_shape="1D_1M", required_roles={"x": "dimension", "y": "measure"},
        ecs_builder="build_funnel", pbi_visual_type="funnel"
    ),
    
    # Cards and KPIs
    "card": ChartDef(
        name="card", display_name="Card",
        synonyms=["single value", "big number", "metric"],
        data_shape="0D_1M", required_roles={"metric": "measure"},
        ecs_builder="build_card", pbi_visual_type="card", supports_dynamic=False
    ),
    "kpi": ChartDef(
        name="kpi", display_name="KPI Visual",
        synonyms=["key performance indicator", "value with trend"],
        data_shape="1D_1M", required_roles={"metric": "measure", "trend": "date"},
        ecs_builder="build_kpi", pbi_visual_type="kpi"
    ),
    
    # Tables
    "table": ChartDef(
        name="table", display_name="Table",
        synonyms=["grid", "list", "data table"],
        data_shape="ND_NM", required_roles={},
        ecs_builder="build_table", pbi_visual_type="tableEx"
    ),
    "matrix": ChartDef(
        name="matrix", display_name="Matrix",
        synonyms=["pivot table", "crosstab"],
        data_shape="2D_NM", required_roles={"rows": "dimension", "columns": "dimension", "values": "measure"},
        ecs_builder="build_matrix", pbi_visual_type="pivotTable"
    )
}

def get_chart_def(chart_name: str) -> Optional[ChartDef]:
    """Retrieve chart definition by primary name or synonym."""
    name_lower = chart_name.lower().strip()
    if name_lower in CHART_REGISTRY:
        return CHART_REGISTRY[name_lower]
    
    for _, cdef in CHART_REGISTRY.items():
        if name_lower in [s.lower() for s in cdef.synonyms]:
            return cdef
            
    return None

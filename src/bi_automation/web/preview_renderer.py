"""
src/bi_automation/web/preview_renderer.py
------------------------------
Generates a self-contained HTML/CSS dashboard preview.

Now uses Apache ECharts (via JSON specs) instead of Matplotlib images.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from config import PALETTE
from dashboard.kpi_detector import KPI
from bi_automation.powerbi.models import ChartSpec
from analysis.insight_engine import Insight

logger = logging.getLogger(__name__)

# ECharts colors
CHART_COLORS = PALETTE["chart_colors"]

class PreviewRenderer:

    def __init__(
        self,
        title: str,
        kpis: List[KPI],
        chart_specs: List[ChartSpec],
        insights: List[Insight],
        data_quality_summary: Dict[str, Any],
        df,
    ):
        self.title                = title
        self.kpis                 = kpis
        self.chart_specs          = chart_specs
        self.insights             = insights
        self.data_quality_summary = data_quality_summary
        self.df                   = df

    def render(self) -> dict:
        """Render preview context for Jinja2 template."""
        chart_options: Dict[str, dict] = {}
        for spec in self.chart_specs:
            option = self._build_echart_option(spec)
            if option:
                chart_options[spec.chart_id] = option

        # We will pass the chart options as a JSON string to the template
        # along with the HTML structural blocks
        charts_json = json.dumps(chart_options)

        # Generate HTML structure for charts
        charts_p1_html = self._build_page_html(1)
        charts_p2_html = self._build_page_html(2)
        charts_p3_html = self._build_page_html(3)
        charts_p4_html = self._build_page_html(4)

        return {
            "title": self.title,
            "kpi_cards_html": self._kpi_cards_html(),
            "charts_p1_html": charts_p1_html,
            "charts_p2_html": charts_p2_html,
            "charts_p3_html": charts_p3_html,
            "charts_p4_html": charts_p4_html,
            "insights_html": self._insights_html(),
            "quality_html": self._quality_html(),
            "echarts_specs_json": charts_json,
        }

    def _build_page_html(self, page: int) -> str:
        specs = [s for s in self.chart_specs if s.page == page]
        if not specs:
            return "<div class='empty-page'>No visuals for this page.</div>"
        
        html = ""
        for spec in specs:
            html += f"<div class='chart-card'>"
            html += f"<div class='chart-title'>{spec.title}</div>"
            # ECharts container
            html += f"<div id='{spec.chart_id}' class='echart-container' style='width:100%; height:300px;'></div>"
            html += "</div>"
        return html

    # ── ECharts Option Builders ───────────────────────────────────────────────
    def _build_echart_option(self, spec: ChartSpec) -> Optional[dict]:
        try:
            ctype = spec.chart_type
            data = spec.data
            
            x_col = spec.x_column or ""
            y_col = spec.y_column or ""
            # Base option
            option = {
                "color": CHART_COLORS,
                "tooltip": {"trigger": "axis" if ctype in ("line", "bar", "multi_line") else "item"},
                "grid": {"left": "8%", "right": "8%", "bottom": "15%", "containLabel": True},
                "xAxis": {
                    "name": x_col,
                    "nameLocation": "center",
                    "nameTextStyle": {"padding": [30, 0, 0, 0]},
                    "axisLabel": {"interval": "auto", "rotate": 45, "hideOverlap": True, "margin": 12},
                    "scale": True
                },
                "yAxis": {
                    "name": y_col,
                    "nameLocation": "center",
                    "nameTextStyle": {"padding": [0, 0, 30, 0]},
                    "axisLabel": {"hideOverlap": True},
                    "scale": True
                },
                "series": []
            }

            if ctype == "line" and data.get("labels"):
                option["xAxis"].update({"type": "category", "data": data["labels"]})
                option["yAxis"].update({"type": "value"})
                option["series"] = [{"data": data["values"], "type": "line", "smooth": True}]
                
            elif ctype == "multi_line" and data:
                labels = list(data.keys())
                if labels and isinstance(data[labels[0]], dict):
                    cat_keys = set()
                    for v in data.values():
                        cat_keys.update(v.keys())
                    cat_list = list(cat_keys)
                    
                    option["legend"] = {"data": cat_list, "bottom": 0}
                    option["xAxis"].update({"type": "category", "data": labels})
                    option["yAxis"].update({"type": "value"})
                    series = []
                    for cat in cat_list:
                        series.append({
                            "name": cat,
                            "type": "line",
                            "data": [data[lbl].get(cat, 0) for lbl in labels]
                        })
                    option["series"] = series

            elif ctype == "bar" and data.get("labels"):
                option["xAxis"].update({"type": "category", "data": data["labels"]})
                option["yAxis"].update({"type": "value"})
                option["series"] = [{"data": data["values"], "type": "bar"}]

            elif ctype == "histogram" and data.get("labels"):
                option["xAxis"].update({"type": "category", "data": data["labels"]})
                option["yAxis"].update({"type": "value"})
                option["series"] = [{"data": data["values"], "type": "bar", "itemStyle": {"color": PALETTE["accent"]}, "barCategoryGap": "0%"}]

            elif ctype == "donut" and data.get("labels"):
                pie_data = [{"name": l, "value": v} for l, v in zip(data["labels"], data["values"])]
                option["xAxis"] = {"show": False}
                option["yAxis"] = {"show": False}
                option["legend"] = {"orient": "vertical", "left": "left"}
                option["series"] = [{
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "data": pie_data
                }]

            elif ctype == "treemap" and data.get("labels"):
                # Echarts treemap uses data: [{name: '', value: ''}]
                tm_data = [{"name": l, "value": v} for l, v in zip(data["labels"], data["values"])]
                option["xAxis"] = {"show": False}
                option["yAxis"] = {"show": False}
                option["series"] = [{
                    "type": "treemap",
                    "data": tm_data,
                    "roam": False
                }]

            elif ctype == "scatter":
                # ECharts scatter requires [[x, y], [x, y]] data
                # Extract directly from self.df!
                if spec.x_column in self.df.columns and spec.y_column in self.df.columns:
                    x_vals = self.df[spec.x_column].dropna()
                    y_vals = self.df[spec.y_column].dropna()
                    # Align indices
                    idx = x_vals.index.intersection(y_vals.index)
                    if len(idx) > 1000:
                        idx = idx[:1000] # Subsample for performance
                    scatter_data = [[float(x_vals[i]), float(y_vals[i])] for i in idx]
                    
                    option["xAxis"].update({"type": "value"})
                    option["yAxis"].update({"type": "value"})
                    option["series"] = [{
                        "type": "scatter",
                        "data": scatter_data,
                        "itemStyle": {"opacity": 0.6}
                    }]
                else:
                    raise KeyError(f"Columns missing for scatter: {spec.x_column}, {spec.y_column}")
                
            elif ctype == "stacked_bar" and data:
                labels = list(data.keys())
                if labels and isinstance(data[labels[0]], dict):
                    cat_keys = set()
                    for v in data.values():
                        cat_keys.update(v.keys())
                    cat_list = list(cat_keys)
                    
                    option["legend"] = {"data": cat_list, "bottom": 0}
                    option["xAxis"] = {"type": "category", "data": labels}
                    option["yAxis"] = {"type": "value"}
                    series = []
                    for cat in cat_list:
                        series.append({
                            "name": cat,
                            "type": "bar",
                            "stack": "total",
                            "data": [data[lbl].get(cat, 0) for lbl in labels]
                        })
                    option["series"] = series
            else:
                return None

            return option
        except Exception as e:
            logger.error("Chart render failed for %s: %s", spec.chart_id, e)
            return None


    # ── HTML Helpers ──────────────────────────────────────────────────────────

    def _kpi_cards_html(self) -> str:
        h = ""
        for k in self.kpis[:8]:
            h += f"<div class='kpi-card'><div class='kpi-title'>{k.title}</div><div class='kpi-value'>{k.formatted_value}</div></div>"
        return h

    def _insights_html(self) -> str:
        if not self.insights:
            return ""
        h = "<div class='section-title'>Key Insights</div><ul class='insight-list'>"
        for ins in self.insights[:5]:
            icon = "&#128161;"
            if ins.priority <= 2: icon = "&#128293;"
            elif ins.priority == 3: icon = "&#9888;&#65039;"
            h += f"<li class='insight-item'><span class='insight-icon'>{icon}</span><span class='insight-text'>{ins.text}</span></li>"
        h += "</ul>"
        return h

    def _quality_html(self) -> str:
        missing = self.data_quality_summary.get("missing_cells", 0)
        dupes   = self.data_quality_summary.get("duplicates", 0)
        outliers= self.data_quality_summary.get("outliers", 0)
        
        h = "<div class='quality-banner'>"
        if missing == 0 and dupes == 0 and outliers == 0:
            h += "<div class='quality-item pass'>&#10004; Data is perfectly clean.</div>"
        else:
            if missing > 0: h += f"<div class='quality-item warn'>&#9888; {missing} missing cells imputed/dropped.</div>"
            if dupes > 0:   h += f"<div class='quality-item warn'>&#9888; {dupes} duplicate rows removed.</div>"
            if outliers > 0:h += f"<div class='quality-item warn'>&#9888; {outliers} potential outliers detected.</div>"
        h += "</div>"
        return h

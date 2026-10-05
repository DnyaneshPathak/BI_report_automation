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
from bi_automation.models.domain import VisualSpec
from analysis.insight_engine import Insight
from bi_automation.models.data_quality import DataQualitySummary

logger = logging.getLogger(__name__)

# ECharts colors
CHART_COLORS = PALETTE["chart_colors"]

class PreviewRenderer:

    def __init__(
        self,
        title: str,
        kpis: List[KPI],
        insights: List[Insight],
        data_quality_summary: Optional[DataQualitySummary],
        df,
        chart_specs: Optional[List[VisualSpec]] = None,
        visual_specs: Optional[List[VisualSpec]] = None,
    ):
        self.title                = title
        self.kpis                 = kpis
        # Accept both kwargs
        self.chart_specs          = visual_specs if visual_specs is not None else (chart_specs or [])
        self.insights             = insights
        self.data_quality_summary = data_quality_summary
        self.df                   = df

    def render(self) -> str:
        """Render a self-contained HTML dashboard preview string."""
        chart_options: Dict[str, dict] = {}
        for spec in self.chart_specs:
            option = self._build_echart_option(spec)
            if option:
                chart_options[spec.id] = option

        charts_json = json.dumps(chart_options)

        # Build chart containers HTML (all visuals, no page split)
        charts_html = self._build_all_charts_html()

        html = f"""
<!DOCTYPE html><html><head><meta charset='utf-8'>
<script src='/static/js/echarts.min.js'></script>""" + f"""
<style>
  body{{font-family:Inter,sans-serif;background:#0f1117;color:#e0e0e0;margin:0;padding:16px;}}
  .dashboard-title{{font-size:22px;font-weight:700;margin-bottom:16px;color:#fff;}}
  .kpi-row{{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:20px;}}
  .kpi-card{{background:#1a1d2e;border-radius:10px;padding:16px 20px;min-width:140px;flex:1;}}
  .kpi-title{{font-size:11px;color:#8888aa;text-transform:uppercase;letter-spacing:.05em;}}
  .kpi-value{{font-size:24px;font-weight:700;color:#6ee7b7;margin-top:4px;}}
  .charts-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:16px;}}
  .chart-card{{background:#1a1d2e;border-radius:10px;padding:14px;overflow:hidden;}}
  .chart-title{{font-size:13px;font-weight:600;margin-bottom:8px;color:#ccd;}}
  .echart-container{{width:100%;height:280px;}}
  .section-title{{font-size:14px;font-weight:600;margin:20px 0 8px;color:#aab;}}
  .quality-banner,.insight-list{{background:#1a1d2e;border-radius:8px;padding:12px;}}
  .insight-item{{display:flex;gap:8px;margin:6px 0;font-size:12px;}}
</style></head><body>
<div class='dashboard-title'>{self.title}</div>
<div class='kpi-row'>{self._kpi_cards_html()}</div>
{self._quality_html()}
<div class='section-title'>📊 Charts &amp; Visuals</div>
<div class='charts-grid'>{charts_html}</div>
{self._insights_html()}
<script>
var _specs = {charts_json};
Object.entries(_specs).forEach(function([id, opt]) {{
  var dom = document.getElementById(id);
  if(dom) {{ var c = echarts.init(dom, 'dark'); c.setOption(opt); }}
}});
</script>
</body></html>"""
        return html

    def _build_all_charts_html(self) -> str:
        """Build HTML chart containers for all visuals."""
        html = ""
        for spec in self.chart_specs:
            has_axes = spec.chart_type not in ("donut", "treemap", "pie", "map")
            significance = spec.reason or ""
            scale_info = ""
            if spec.measure and spec.measure != "Count":
                scale_info = f"Scale: {spec.measure} (Agg: {spec.aggregation or 'value'})"
            elif spec.measure == "Count":
                scale_info = "Scale: Frequency/Count"
                
            html += f"<div class='chart-card'>"
            html += f"<div class='chart-title'>{spec.title}</div>"
            html += f"<div style='font-size:0.85rem; color:#64748b; margin-top:2px; margin-bottom:12px; line-height:1.4;'>"
            if significance:
                html += f"<strong>Significance:</strong> {significance}<br>"
            if scale_info:
                html += f"<strong>{scale_info}</strong>"
            if has_axes:
                html += f"<br><em>(Zoom/pan using bottom slider)</em>"
            html += "</div>"
            html += f"<div id='{spec.id}' class='echart-container'></div>"
            html += "</div>"
        return html

    def _build_page_html(self, page: int) -> str:
        """Legacy page-based html builder (kept for compatibility)."""
        specs = [s for s in self.chart_specs if (s.page or 1) == page]
        if not specs:
            return "<div class='empty-page'>No visuals for this page.</div>"
        html = ""
        for spec in specs:
            has_axes = spec.chart_type not in ("donut", "treemap", "pie", "map")
            html += f"<div class='chart-card'>"
            html += f"<div class='chart-title'>{spec.title}</div>"
            if has_axes:
                html += f"<div style='font-size:11px; color:#64748b; margin-top:-4px; margin-bottom:8px;'>(Scale / Zoom using bottom slider)</div>"
            html += f"<div id='{spec.id}' class='echart-container' style='width:100%; height:300px;'></div>"
            html += "</div>"
        return html

    # ── ECharts Option Builders ───────────────────────────────────────────────
    def _build_echart_option(self, spec: VisualSpec) -> Optional[dict]:
        try:
            ctype = spec.chart_type
            data = spec.data
            
            x_col = spec.dimension or ""
            y_col = spec.measure or ""
            agg_label = (spec.aggregation or "").upper() if hasattr(spec, 'aggregation') and spec.aggregation else ""
            if y_col in ("Count", "Frequency"):
                y_axis_name = y_col
            elif y_col:
                y_axis_name = f"{agg_label}({y_col})" if agg_label else y_col
            else:
                y_axis_name = ""

            # Determine if chart uses cartesian axes
            has_axes = ctype not in ("donut", "treemap", "pie", "map")

            # Base option
            option = {
                "color": CHART_COLORS,
                "tooltip": {"trigger": "axis" if ctype in ("line", "bar", "area", "multi_line") else "item"},
                "series": []
            }
            
            if has_axes:
                option["grid"] = {"left": "15%", "right": "5%", "bottom": "25%", "top": "12%", "containLabel": True}
                option["dataZoom"] = [{"type": "inside"}, {"type": "slider", "height": 20, "bottom": 10}]
                option["xAxis"] = {
                    "name": x_col,
                    "nameLocation": "center",
                    "nameGap": 35,
                    "nameTextStyle": {"fontSize": 11, "fontWeight": "bold"},
                    "axisLabel": {"interval": "auto", "rotate": 45, "hideOverlap": True, "margin": 10, "fontSize": 10},
                    "scale": True
                }
                option["yAxis"] = {
                    "name": y_axis_name,
                    "nameLocation": "middle",
                    "nameRotate": 90,
                    "nameGap": 65,
                    "nameTextStyle": {"fontSize": 11, "fontWeight": "bold"},
                    "axisLabel": {"hideOverlap": True, "fontSize": 10},
                    "scale": True
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

            elif ctype == "pie" and data.get("labels"):
                pie_data = [{"name": l, "value": v} for l, v in zip(data["labels"], data["values"])]
                option["xAxis"] = {"show": False}
                option["yAxis"] = {"show": False}
                option["legend"] = {"orient": "vertical", "left": "left"}
                option["series"] = [{
                    "type": "pie",
                    "radius": "70%",
                    "data": pie_data
                }]

            elif ctype == "funnel" and data.get("labels"):
                funnel_data = [{"name": l, "value": v} for l, v in zip(data["labels"], data["values"])]
                option["xAxis"] = {"show": False}
                option["yAxis"] = {"show": False}
                option["legend"] = {"orient": "vertical", "left": "left"}
                option["series"] = [{
                    "type": "funnel",
                    "left": "10%",
                    "width": "80%",
                    "data": funnel_data
                }]

            elif ctype == "waterfall" and data.get("labels"):
                # Echarts doesn't have a native waterfall, we emulate it with a transparent bar and a solid bar
                # But a simple bar is fine as fallback if we don't want to calculate offsets
                option["xAxis"].update({"type": "category", "data": data["labels"]})
                option["yAxis"].update({"type": "value"})
                option["series"] = [{"data": data["values"], "type": "bar"}]

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

            elif ctype == "area" and data.get("labels"):
                option["xAxis"].update({"type": "category", "data": data["labels"]})
                option["yAxis"].update({"type": "value"})
                option["series"] = [{
                    "data": data["values"], "type": "line", "smooth": True,
                    "areaStyle": {"opacity": 0.4}
                }]

            elif ctype == "heatmap" and data.get("labels"):
                # Simple bar fallback for heatmap until full matrix data is available
                option["xAxis"].update({"type": "category", "data": data["labels"]})
                option["yAxis"].update({"type": "value"})
                option["series"] = [{"data": data["values"], "type": "bar"}]

            elif ctype == "scatter":
                # Prefer pre-computed data from DescriptionPlanner
                if data.get("x") and data.get("y"):
                    scatter_data = list(zip(data["x"], data["y"]))
                elif spec.dimension in self.df.columns and spec.measure in self.df.columns:
                    x_vals = self.df[spec.dimension].dropna()
                    y_vals = self.df[spec.measure].dropna()
                    idx = x_vals.index.intersection(y_vals.index)[:1000]
                    scatter_data = [[float(x_vals[i]), float(y_vals[i])] for i in idx]
                else:
                    raise KeyError(f"Columns missing for scatter: {spec.dimension}, {spec.measure}")

                option["xAxis"].update({"type": "value", "name": x_col})
                option["yAxis"].update({"type": "value", "name": y_col})
                option["series"] = [{
                    "type": "scatter",
                    "data": scatter_data,
                    "symbolSize": 6,
                    "itemStyle": {"opacity": 0.6}
                }]
                
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
            logger.error("Chart render failed for %s: %s", spec.id, e)
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
        if not self.data_quality_summary:
            return ""
        missing = self.data_quality_summary.missing_cells
        dupes   = self.data_quality_summary.duplicate_rows
        outliers= self.data_quality_summary.outlier_count
        
        h = "<div class='quality-banner'>"
        if missing == 0 and dupes == 0 and outliers == 0:
            h += "<div class='quality-item pass'>&#10004; Data is perfectly clean.</div>"
        else:
            if missing > 0: h += f"<div class='quality-item warn'>&#9888; {missing} missing cells imputed/dropped.</div>"
            if dupes > 0:   h += f"<div class='quality-item warn'>&#9888; {dupes} duplicate rows removed.</div>"
            if outliers > 0:h += f"<div class='quality-item warn'>&#9888; {outliers} potential outliers detected.</div>"
        h += "</div>"
        return h

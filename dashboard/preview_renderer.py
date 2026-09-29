"""
dashboard/preview_renderer.py
------------------------------
Generates a self-contained HTML/CSS dashboard preview.

Everything is rendered locally using Matplotlib + Jinja2.
No data is sent externally.
Charts are embedded as base64 PNG images.
"""

from __future__ import annotations

import base64
import io
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")   # non-interactive backend — no GUI window
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from config import PALETTE, TEMP_DIR
from dashboard.kpi_detector import KPI
from dashboard.chart_selector import ChartSpec
from analysis.insight_engine import Insight

logger = logging.getLogger(__name__)

# ── Chart colour cycle ────────────────────────────────────────────────────────
CHART_COLORS = PALETTE["chart_colors"]
NAVY    = PALETTE["primary"]
BLUE    = PALETTE["secondary"]
BG      = PALETTE["background"]
SURFACE = PALETTE["surface"]
BORDER  = PALETTE["border"]
TEXT    = PALETTE["text_primary"]
MUTED   = PALETTE["text_secondary"]


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

    def render(self) -> str:
        """Render preview as a self-contained HTML string."""
        chart_images: Dict[str, str] = {}
        for spec in self.chart_specs:
            img = self._render_chart(spec)
            if img:
                chart_images[spec.chart_id] = img

        html = self._build_html(chart_images)
        return html

    # ── Individual chart rendering ────────────────────────────────────────────
    def _render_chart(self, spec: ChartSpec) -> Optional[str]:
        try:
            fig, ax = plt.subplots(figsize=(6, 3.5), facecolor=SURFACE)
            ax.set_facecolor(SURFACE)
            for spine in ax.spines.values():
                spine.set_edgecolor(BORDER)

            ctype = spec.chart_type
            data  = spec.data

            if ctype == "line" and data.get("labels"):
                self._line_chart(ax, data["labels"], data["values"], spec.title)
            elif ctype == "multi_line" and data:
                self._multi_line_chart(ax, data, spec.title)
            elif ctype == "bar" and data.get("labels"):
                self._bar_chart(ax, data["labels"], data["values"], spec.title, horizontal=False)
            elif ctype == "histogram" and data.get("labels"):
                self._bar_chart(ax, data["labels"], data["values"], spec.title, horizontal=False, color=PALETTE["accent"])
            elif ctype == "donut" and data.get("labels"):
                self._donut_chart(fig, ax, data["labels"], data["values"], spec.title)
            elif ctype == "treemap" and data.get("labels"):
                self._bar_chart(ax, data["labels"][:10], data["values"][:10], spec.title, horizontal=True)
            elif ctype == "scatter":
                self._scatter_chart(ax, spec)
            elif ctype == "stacked_bar" and data:
                self._stacked_bar_chart(ax, data, spec.title)
            else:
                plt.close(fig)
                return None

            plt.tight_layout(pad=0.5)
            img_b64 = self._fig_to_base64(fig)
            plt.close(fig)
            return img_b64
        except Exception as exc:
            logger.warning("Chart render failed for %s: %s", spec.chart_id, exc)
            try:
                plt.close("all")
            except Exception:
                pass
            return None

    # ── Chart type implementations ────────────────────────────────────────────
    def _line_chart(self, ax, labels, values, title):
        x = range(len(labels))
        ax.plot(x, values, color=BLUE, linewidth=2, marker="o", markersize=3)
        ax.fill_between(x, values, alpha=0.1, color=BLUE)
        ax.set_title(title, fontsize=9, fontweight="bold", color=TEXT, pad=6)
        ax.tick_params(labelsize=6, colors=MUTED)
        step = max(1, len(labels) // 8)
        ax.set_xticks(list(x)[::step])
        ax.set_xticklabels(labels[::step], rotation=30, ha="right", fontsize=6)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(self._fmt_tick))
        ax.grid(axis="y", alpha=0.3, linestyle="--")

    def _multi_line_chart(self, ax, pivot: Dict, title):
        colors = CHART_COLORS
        all_periods = sorted({p for series in pivot.values() for p in series.keys()})
        for i, (group, series) in enumerate(list(pivot.items())[:6]):
            values = [series.get(p, 0) for p in all_periods]
            ax.plot(range(len(all_periods)), values,
                    label=str(group), color=colors[i % len(colors)], linewidth=1.8)
        ax.set_title(title, fontsize=9, fontweight="bold", color=TEXT, pad=6)
        ax.legend(fontsize=6, loc="upper left")
        step = max(1, len(all_periods) // 8)
        ax.set_xticks(list(range(len(all_periods)))[::step])
        ax.set_xticklabels(all_periods[::step], rotation=30, ha="right", fontsize=6)
        ax.tick_params(labelsize=6, colors=MUTED)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(self._fmt_tick))
        ax.grid(axis="y", alpha=0.3, linestyle="--")

    def _bar_chart(self, ax, labels, values, title, horizontal=False, color=None):
        color = color or BLUE
        n = len(labels)
        if horizontal:
            ax.barh(range(n), values, color=color, alpha=0.85)
            ax.set_yticks(range(n))
            ax.set_yticklabels([str(l)[:20] for l in labels], fontsize=7)
            ax.xaxis.set_major_formatter(mticker.FuncFormatter(self._fmt_tick))
        else:
            ax.bar(range(n), values, color=color, alpha=0.85)
            ax.set_xticks(range(n))
            ax.set_xticklabels([str(l)[:12] for l in labels], rotation=30, ha="right", fontsize=7)
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(self._fmt_tick))
        ax.set_title(title, fontsize=9, fontweight="bold", color=TEXT, pad=6)
        ax.tick_params(labelsize=6, colors=MUTED)
        ax.grid(axis="x" if horizontal else "y", alpha=0.3, linestyle="--")

    def _donut_chart(self, fig, ax, labels, values, title):
        colors = CHART_COLORS[: len(labels)]
        wedges, _ = ax.pie(
            values, labels=None, colors=colors,
            startangle=90, wedgeprops=dict(width=0.55),
        )
        ax.legend(
            wedges, [str(l)[:15] for l in labels],
            loc="center left", bbox_to_anchor=(0.85, 0.5), fontsize=6,
        )
        ax.set_title(title, fontsize=9, fontweight="bold", color=TEXT, pad=6)

    def _scatter_chart(self, ax, spec: ChartSpec):
        try:
            x = self.df[spec.x_column].pipe(lambda s: s if hasattr(s, "dtype") else s)
            y = self.df[spec.y_column].pipe(lambda s: s if hasattr(s, "dtype") else s)
            import pandas as pd
            x = pd.to_numeric(x, errors="coerce")
            y = pd.to_numeric(y, errors="coerce")
            mask = x.notna() & y.notna()
            x, y = x[mask].values, y[mask].values
            sample = min(500, len(x))
            idx = np.random.choice(len(x), sample, replace=False)
            ax.scatter(x[idx], y[idx], alpha=0.5, color=BLUE, s=10)
            r = spec.data.get("pearson_r", "")
            ax.set_title(f"{spec.title}\n(r = {r})", fontsize=9, fontweight="bold", color=TEXT, pad=6)
            ax.tick_params(labelsize=6, colors=MUTED)
            ax.xaxis.set_major_formatter(mticker.FuncFormatter(self._fmt_tick))
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(self._fmt_tick))
        except Exception:
            pass

    def _stacked_bar_chart(self, ax, pivot: Dict, title):
        import numpy as np
        categories = list(pivot.keys())[:10]
        sub_cats   = list(list(pivot.values())[0].keys())[:6] if pivot else []
        x = np.arange(len(categories))
        bottom = np.zeros(len(categories))
        for i, sub in enumerate(sub_cats):
            vals = [pivot[cat].get(sub, 0) for cat in categories]
            ax.bar(x, vals, bottom=bottom, label=str(sub)[:12],
                   color=CHART_COLORS[i % len(CHART_COLORS)], alpha=0.85)
            bottom += np.array(vals)
        ax.set_xticks(x)
        ax.set_xticklabels([str(c)[:12] for c in categories], rotation=30, ha="right", fontsize=7)
        ax.set_title(title, fontsize=9, fontweight="bold", color=TEXT, pad=6)
        ax.legend(fontsize=6, loc="upper right")
        ax.tick_params(labelsize=6, colors=MUTED)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(self._fmt_tick))
        ax.grid(axis="y", alpha=0.3, linestyle="--")

    # ── HTML generation ───────────────────────────────────────────────────────
    def _build_html(self, chart_images: Dict[str, str]) -> str:
        kpi_cards_html  = self._kpi_cards_html()
        charts_p1_html  = self._page_charts_html(chart_images, page=1)
        charts_p2_html  = self._page_charts_html(chart_images, page=2)
        charts_p3_html  = self._page_charts_html(chart_images, page=3)
        charts_p4_html  = self._page_charts_html(chart_images, page=4)
        insights_html   = self._insights_html()
        quality_html    = self._quality_html()

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{self.title} — Dashboard Preview</title>
<style>
  :root {{
    --navy:   {NAVY};
    --blue:   {BLUE};
    --bg:     {BG};
    --surface:{SURFACE};
    --border: {BORDER};
    --text:   {TEXT};
    --muted:  {MUTED};
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); }}
  .db-header {{
    background: linear-gradient(135deg, var(--navy) 0%, #1e3a6e 100%);
    color: #fff; padding: 18px 32px;
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 3px solid var(--blue);
  }}
  .db-header h1 {{ font-size: 1.3rem; font-weight: 700; letter-spacing: 0.02em; }}
  .db-header .meta {{ font-size: 0.75rem; opacity: 0.7; }}
  .db-body {{ padding: 24px 32px; }}
  /* KPI Cards */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px; margin-bottom: 24px;
  }}
  .kpi-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 18px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: transform 0.15s, box-shadow 0.15s;
  }}
  .kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,0,0,0.12); }}
  .kpi-icon {{ font-size: 1.5rem; margin-bottom: 6px; }}
  .kpi-value {{ font-size: 1.6rem; font-weight: 800; color: var(--navy); line-height: 1.1; }}
  .kpi-title {{ font-size: 0.72rem; color: var(--muted); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.06em; }}
  /* Section headers */
  .section-title {{
    font-size: 0.8rem; font-weight: 700; color: var(--muted);
    text-transform: uppercase; letter-spacing: 0.1em;
    margin: 28px 0 12px; padding-bottom: 6px;
    border-bottom: 2px solid var(--border);
  }}
  /* Charts */
  .chart-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    gap: 18px; margin-bottom: 24px;
  }}
  .chart-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    overflow: hidden;
  }}
  .chart-card img {{ width: 100%; border-radius: 6px; }}
  .chart-card .empty-chart {{
    height: 160px; display: flex; align-items: center; justify-content: center;
    background: var(--bg); border-radius: 6px; color: var(--muted); font-size: 0.8rem;
  }}
  /* Tabs */
  .tabs {{ display: flex; gap: 4px; margin-bottom: 18px; flex-wrap: wrap; }}
  .tab-btn {{
    padding: 7px 18px; border: 1px solid var(--border); border-radius: 20px;
    background: var(--surface); color: var(--muted); cursor: pointer;
    font-size: 0.78rem; font-weight: 600; transition: all 0.15s;
  }}
  .tab-btn.active {{ background: var(--navy); color: #fff; border-color: var(--navy); }}
  .tab-content {{ display: none; }}
  .tab-content.active {{ display: block; }}
  /* Insights */
  .insight-panel {{
    background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%);
    border: 1px solid #c7d7fd; border-radius: 12px; padding: 20px 24px;
    margin-bottom: 24px;
  }}
  .insight-panel h3 {{ font-size: 0.8rem; font-weight: 700; color: var(--navy); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px; }}
  .insight-item {{ display: flex; gap: 10px; margin-bottom: 8px; font-size: 0.83rem; color: var(--text); }}
  .insight-bullet {{ color: var(--blue); font-weight: 700; flex-shrink: 0; }}
  /* Quality */
  .quality-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 24px; }}
  .quality-item {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; }}
  .quality-label {{ font-size: 0.68rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }}
  .quality-value {{ font-size: 1.1rem; font-weight: 700; color: var(--navy); margin-top: 2px; }}
  /* Approval buttons */
  .action-bar {{
    position: sticky; bottom: 0; background: rgba(255,255,255,0.95);
    backdrop-filter: blur(8px);
    border-top: 1px solid var(--border);
    padding: 16px 32px; display: flex; gap: 16px; align-items: center;
    justify-content: center; z-index: 100;
  }}
  .btn {{ padding: 12px 28px; border-radius: 8px; border: none; cursor: pointer; font-size: 0.9rem; font-weight: 700; transition: all 0.15s; }}
  .btn-primary {{ background: var(--navy); color: #fff; }}
  .btn-primary:hover {{ background: #0f1e38; transform: translateY(-1px); box-shadow: 0 4px 16px rgba(27,42,74,0.3); }}
  .btn-secondary {{ background: var(--surface); color: var(--navy); border: 2px solid var(--navy); }}
  .btn-secondary:hover {{ background: #f0f4ff; }}
  /* Feedback panel */
  .feedback-panel {{
    background: #fffbeb; border-top: 1px solid #fde68a;
    padding: 16px 32px;
  }}
  .feedback-toggle {{
    background: none; border: none; cursor: pointer;
    font-size: 0.82rem; font-weight: 700; color: var(--navy);
    display: flex; align-items: center; gap: 6px;
    padding: 0; margin: 0 auto 0 0;
  }}
  .feedback-toggle:hover {{ color: var(--blue); }}
  .feedback-body {{ display: none; margin-top: 12px; }}
  .feedback-body.open {{ display: block; }}
  .feedback-label {{ font-size: 0.78rem; font-weight: 700; color: var(--navy); margin-bottom: 6px; display: block; }}
  .feedback-textarea {{
    width: 100%; min-height: 80px; padding: 10px 14px;
    border: 1px solid var(--border); border-radius: 8px;
    font-family: 'Segoe UI', system-ui, sans-serif; font-size: 0.85rem;
    color: var(--text); background: var(--surface); resize: vertical;
    outline: none; transition: border-color 0.15s;
  }}
  .feedback-textarea:focus {{ border-color: var(--blue); }}
  .feedback-hints {{ font-size: 0.7rem; color: var(--muted); margin-top: 6px; }}
  .feedback-hints span {{ background: #f1f5f9; border-radius: 4px; padding: 2px 8px; margin: 2px; display: inline-block; cursor: pointer; transition: background 0.1s; }}
  .feedback-hints span:hover {{ background: #dbeafe; color: var(--blue); }}
  .interpreted-msg {{ font-size: 0.75rem; color: #166534; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 8px 12px; margin-top: 8px; display: none; }}
</style>
</head>
<body>

<div class="db-header">
  <h1>📊 {self.title}</h1>
  <div class="meta">Dashboard Preview · Local Analysis · All data remains on this machine</div>
</div>

<div class="db-body">

  <!-- Quality Summary -->
  <div class="section-title">Data Quality Summary</div>
  {quality_html}

  <!-- KPIs -->
  <div class="section-title">Key Performance Indicators</div>
  <div class="kpi-grid">{kpi_cards_html}</div>

  <!-- Key Insights -->
  {insights_html}

  <!-- Dashboard Pages -->
  <div class="section-title">Dashboard Pages</div>
  <div class="tabs">
    <button class="tab-btn active" onclick="showTab('p1',this)">Executive Overview</button>
    <button class="tab-btn" onclick="showTab('p2',this)">Detailed Analysis</button>
    <button class="tab-btn" onclick="showTab('p3',this)">Trend Analysis</button>
    <button class="tab-btn" onclick="showTab('p4',this)">Statistical Insights</button>
  </div>

  <div id="tab-p1" class="tab-content active">
    <div class="chart-grid">{charts_p1_html}</div>
  </div>
  <div id="tab-p2" class="tab-content">
    <div class="chart-grid">{charts_p2_html}</div>
  </div>
  <div id="tab-p3" class="tab-content">
    <div class="chart-grid">{charts_p3_html}</div>
  </div>
  <div id="tab-p4" class="tab-content">
    <div class="chart-grid">{charts_p4_html}</div>
  </div>

</div>

<!-- Feedback panel -->
<div class="feedback-panel" id="feedback-panel">
  <button class="feedback-toggle" onclick="toggleFeedback()" id="toggle-btn">
    <span id="toggle-icon">&#9654;</span>&nbsp; Request Changes Before Regenerating
  </button>
  <div class="feedback-body" id="feedback-body">
    <label class="feedback-label" for="feedback-text">Describe what you want changed in the dashboard:</label>
    <textarea
      class="feedback-textarea"
      id="feedback-text"
      placeholder="e.g. Remove scatter plots. Add a pie chart for Category. Focus on Revenue trends. Show top 5 Regions. Show distribution of Sales. Add line chart for Date vs Profit."
    ></textarea>
    <div class="feedback-hints">
      <strong style="font-size:0.7rem;color:var(--muted)">Quick inserts:</strong>
      <span onclick="insertHint('Remove scatter plots')">Remove scatter plots</span>
      <span onclick="insertHint('Add pie chart for ')">Add pie chart for...</span>
      <span onclick="insertHint('Focus on ')">Focus on column...</span>
      <span onclick="insertHint('Show top 5 categories')">Show top 5</span>
      <span onclick="insertHint('Add bar chart for ')">Add bar chart for...</span>
      <span onclick="insertHint('Show distribution of ')">Distribution of...</span>
      <span onclick="insertHint('Trend of ')">Trend of...</span>
      <span onclick="insertHint('Show correlation between  and ')">Correlation between...</span>
    </div>
    <div class="interpreted-msg" id="interp-msg"></div>
  </div>
</div>

<!-- Approval action bar -->
<div class="action-bar">
  <button class="btn btn-primary" id="btn-approve" onclick="approveAndGenerate()">
    &#x2705; Approve &amp; Generate Power BI
  </button>
  <button class="btn btn-secondary" id="btn-regen" onclick="regenerate()">
    &#x1F504; Regenerate Dashboard
  </button>
</div>

<script>
function showTab(tabId, el) {{
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + tabId).classList.add('active');
  el.classList.add('active');
}}
function toggleFeedback() {{
  const body = document.getElementById('feedback-body');
  const icon = document.getElementById('toggle-icon');
  body.classList.toggle('open');
  icon.innerHTML = body.classList.contains('open') ? '&#9660;' : '&#9654;';
}}
function insertHint(text) {{
  const ta = document.getElementById('feedback-text');
  ta.value = ta.value ? ta.value.trimEnd() + ' ' + text : text;
  ta.focus();
  // Auto-open feedback panel
  const body = document.getElementById('feedback-body');
  if (!body.classList.contains('open')) toggleFeedback();
}}
function approveAndGenerate() {{
  document.getElementById('btn-approve').textContent = 'Generating...';
  document.getElementById('btn-approve').disabled = true;
  fetch('/approve', {{method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{action:'approve'}})}})
    .then(r => r.json())
    .then(d => {{
      if(d.success) {{
        window.location.href = '/complete';
      }} else {{
        alert('Error: ' + d.error);
        document.getElementById('btn-approve').textContent = 'Approve & Generate Power BI';
        document.getElementById('btn-approve').disabled = false;
      }}
    }})
    .catch(e => {{
      alert('Error: ' + e);
      document.getElementById('btn-approve').textContent = 'Approve & Generate Power BI';
      document.getElementById('btn-approve').disabled = false;
    }});
}}
function regenerate() {{
  const feedback = document.getElementById('feedback-text').value.trim();
  const btn = document.getElementById('btn-regen');
  btn.textContent = 'Regenerating...';
  btn.disabled = true;
  const interpMsg = document.getElementById('interp-msg');
  interpMsg.style.display = 'none';
  fetch('/regenerate', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{feedback: feedback}})
  }})
    .then(r => r.json())
    .then(d => {{
      if(d.success) {{
        if(d.interpreted) {{
          interpMsg.textContent = 'Applied: ' + d.interpreted;
          interpMsg.style.display = 'block';
          setTimeout(() => window.location.reload(), 1200);
        }} else {{
          window.location.reload();
        }}
      }} else {{
        alert('Error: ' + (d.error || 'Unknown error'));
        btn.textContent = 'Regenerate Dashboard';
        btn.disabled = false;
      }}
    }})
    .catch(e => {{
      alert('Error: ' + e);
      btn.textContent = 'Regenerate Dashboard';
      btn.disabled = false;
    }});
}}
</script>
</body>
</html>"""

    # ── HTML fragment builders ─────────────────────────────────────────────────
    def _kpi_cards_html(self) -> str:
        if not self.kpis:
            return "<p style='color:var(--muted);font-size:0.8rem;'>No KPIs detected.</p>"
        cards = []
        for kpi in self.kpis[:6]:
            cards.append(f"""
<div class="kpi-card">
  <div class="kpi-icon">{kpi.icon}</div>
  <div class="kpi-value">{kpi.formatted_value}</div>
  <div class="kpi-title">{kpi.title}</div>
</div>""")
        return "\n".join(cards)

    def _page_charts_html(self, chart_images: Dict[str, str], page: int) -> str:
        page_specs = [s for s in self.chart_specs if s.page == page]
        if not page_specs:
            return "<div class='chart-card'><div class='empty-chart'>No charts available for this page.</div></div>"
        cards = []
        for spec in page_specs:
            img_b64 = chart_images.get(spec.chart_id)
            if img_b64:
                cards.append(f"""
<div class="chart-card">
  <img src="data:image/png;base64,{img_b64}" alt="{spec.title}">
</div>""")
            else:
                cards.append(f"""
<div class="chart-card">
  <div class="empty-chart">{spec.title} (preview unavailable)</div>
</div>""")
        return "\n".join(cards)

    def _insights_html(self) -> str:
        if not self.insights:
            return ""
        items = []
        for ins in self.insights[:8]:
            items.append(f'<div class="insight-item"><span class="insight-bullet">•</span><span>{ins.text}</span></div>')
        return f"""
<div class="insight-panel">
  <h3>🔍 Key Insights</h3>
  {"".join(items)}
</div>"""

    def _quality_html(self) -> str:
        q = self.data_quality_summary
        items = [
            ("Rows",          str(q.get("rows", "—"))),
            ("Columns",       str(q.get("columns", "—"))),
            ("Missing",       f"{q.get('missing_pct', 0):.1f}%"),
            ("Duplicates",    f"{q.get('duplicate_pct', 0):.1f}%"),
            ("Numeric Fields",str(q.get("numeric_count", "—"))),
            ("Categorical",   str(q.get("categorical_count", "—"))),
            ("Date Fields",   str(q.get("date_count", "—"))),
            ("Outliers",      str(q.get("outlier_count", "—"))),
        ]
        html_items = "".join(
            f'<div class="quality-item"><div class="quality-label">{label}</div><div class="quality-value">{value}</div></div>'
            for label, value in items
        )
        return f'<div class="quality-grid">{html_items}</div>'

    # ── Utility ───────────────────────────────────────────────────────────────
    @staticmethod
    def _fig_to_base64(fig) -> str:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                    facecolor=SURFACE, edgecolor="none")
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("ascii")

    @staticmethod
    def _fmt_tick(x, _):
        if abs(x) >= 1_000_000:
            return f"{x/1_000_000:.1f}M"
        elif abs(x) >= 1_000:
            return f"{x/1_000:.0f}K"
        else:
            return f"{x:,.0f}"

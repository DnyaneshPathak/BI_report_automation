"""
powerbi/model_builder.py
--------------------------
Builds the Power BI data model as a Power BI Project (.pbip) structure.

Produces:
  - Dataset BIM (Tabular Model JSON)
  - Report layout JSON
  - Date table definition
  - Relationships
  - DAX measures embedded in the model

The .pbip is later saved via Power BI Desktop into a .pbix.
"""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from preprocessing.datatype_detector import ColumnProfile
from dashboard.dax_generator import DAXMeasure
from dashboard.kpi_detector import KPI
from bi_automation.models.domain import VisualSpec
from config import TEMP_DIR

logger = logging.getLogger(__name__)


class ModelBuilder:

    def __init__(
        self,
        df: pd.DataFrame,
        profiles: Dict[str, ColumnProfile],
        dax_measures: List[DAXMeasure],
        kpis: List[KPI],
        chart_specs: List[VisualSpec],
        dashboard_title: str,
        table_name: str = "DataTable",
    ):
        self.df              = df
        self.profiles        = profiles
        self.dax_measures    = dax_measures
        self.kpis            = kpis
        self.chart_specs     = chart_specs
        self.dashboard_title = dashboard_title
        self.table_name      = table_name

    def build(self, output_dir: Path) -> Path:
        """
        Build a Power BI Project directory (.pbip compatible).
        Returns the path to the project directory.
        """
        project_dir = output_dir / f"{self.dashboard_title.replace(' ', '_')}_Project"
        project_dir.mkdir(parents=True, exist_ok=True)

        dataset_dir = project_dir / "DataSet"
        dataset_dir.mkdir(exist_ok=True)

        report_dir = project_dir / "Report"
        report_dir.mkdir(exist_ok=True)

        # Write dataset model JSON (Tabular BIM-like)
        model = self._build_dataset_model()
        with open(dataset_dir / "model.bim", "w", encoding="utf-8") as f:
            json.dump(model, f, indent=2)

        # Write report layout JSON
        layout = self._build_report_layout()
        with open(report_dir / "report.json", "w", encoding="utf-8") as f:
            json.dump(layout, f, indent=2)

        # Write .pbip project file
        pbip = {
            "version": "1.0",
            "artifacts": [
                {"report": {"path": "Report"}},
                {"dataset": {"path": "DataSet"}},
            ],
            "settings": {"enableAutoRecovery": True},
        }
        with open(project_dir / f"{self.dashboard_title}.pbip", "w", encoding="utf-8") as f:
            json.dump(pbip, f, indent=2)

        logger.info("Power BI Project written to: %s", project_dir)
        return project_dir

    # ── Dataset model (Tabular BIM) ───────────────────────────────────────────
    def _build_dataset_model(self) -> dict:
        columns = []
        for col, profile in self.profiles.items():
            if col not in self.df.columns:
                continue
            dt = self._pbi_datatype(profile.analytical_type)
            col_def = {
                "name": col,
                "dataType": dt,
                "sourceColumn": col,
                "summarizeBy": self._summarize_by(profile),
                "annotations": [{"name": "AnalyticalType", "value": profile.analytical_type}],
            }
            if profile.analytical_type == "datetime":
                col_def["formatString"] = "yyyy-MM-dd"
            columns.append(col_def)

        # DAX measures
        measures = []
        for m in self.dax_measures:
            measures.append({
                "name": m.name,
                "expression": m.expression,
                "formatString": "#,##0.00",
                "annotations": [{"name": "Category", "value": m.category}],
            })

        tables = [
            {
                "name": self.table_name,
                "columns": columns,
                "measures": measures,
                "partitions": [
                    {
                        "name": "Partition",
                        "source": {
                            "type": "m",
                            "expression": [
                                f'let',
                                f'    Source = Excel.Workbook(File.Contents("{{SOURCE_PATH}}"), null, true),',
                                f'    Sheet = Source{{[Item="{{SHEET_NAME}}",Kind="Sheet"]}}[Data],',
                                f'    PromotedHeaders = Table.PromoteHeaders(Sheet, [PromoteAllScalars=true])',
                                f'in',
                                f'    PromotedHeaders',
                            ],
                        },
                    }
                ],
            }
        ]

        # Date table (calendar)
        date_cols = [c for c, p in self.profiles.items() if p.analytical_type == "datetime" and c in self.df.columns]
        if date_cols:
            tables.append(self._date_table_definition())

        return {
            "compatibilityLevel": 1550,
            "model": {
                "culture": "en-US",
                "tables": tables,
                "relationships": self._build_relationships(date_cols),
                "annotations": [{"name": "DashboardTitle", "value": self.dashboard_title}],
            },
        }

    def _date_table_definition(self) -> dict:
        return {
            "name": "DateTable",
            "isHidden": False,
            "columns": [
                {"name": "Date",        "dataType": "dateTime", "sourceColumn": "Date",        "isKey": True},
                {"name": "Year",        "dataType": "int64",    "sourceColumn": "Year"},
                {"name": "Quarter",     "dataType": "string",   "sourceColumn": "Quarter"},
                {"name": "Month",       "dataType": "int64",    "sourceColumn": "Month"},
                {"name": "MonthName",   "dataType": "string",   "sourceColumn": "MonthName"},
                {"name": "Day",         "dataType": "int64",    "sourceColumn": "Day"},
                {"name": "DayOfWeek",   "dataType": "int64",    "sourceColumn": "DayOfWeek"},
                {"name": "WeekNumber",  "dataType": "int64",    "sourceColumn": "WeekNumber"},
            ],
            "partitions": [
                {
                    "name": "DatePartition",
                    "source": {
                        "type": "calculated",
                        "expression": [
                            "CALENDAR(",
                            f"  MINX('{self.table_name}', MINX(ROW(\"x\",1), DATE(2000,1,1))),",
                            f"  MAXX('{self.table_name}', MAXX(ROW(\"x\",1), TODAY()))",
                            ")",
                        ],
                    },
                }
            ],
            "calculatedColumns": [
                {"name": "Year",       "expression": "YEAR([Date])"},
                {"name": "Month",      "expression": "MONTH([Date])"},
                {"name": "MonthName",  "expression": "FORMAT([Date], \"MMM\")"},
                {"name": "Quarter",    "expression": "\"Q\" & QUARTER([Date])"},
                {"name": "Day",        "expression": "DAY([Date])"},
                {"name": "DayOfWeek",  "expression": "WEEKDAY([Date])"},
                {"name": "WeekNumber", "expression": "WEEKNUM([Date])"},
            ],
            "isDateTable": True,
        }

    def _build_relationships(self, date_cols: List[str]) -> List[dict]:
        rels = []
        for dc in date_cols[:1]:
            rels.append({
                "name": f"rel_DateTable_{dc}",
                "fromTable": "DateTable",
                "fromColumn": "Date",
                "toTable": self.table_name,
                "toColumn": dc,
                "crossFilteringBehavior": "oneDirection",
                "fromCardinality": "one",
                "toCardinality": "many",
            })
        return rels

    # ── Report layout ─────────────────────────────────────────────────────────
    def _build_report_layout(self) -> dict:
        sections = []
        pages = {1: "Executive Overview", 2: "Detailed Analysis", 3: "Trend Analysis", 4: "Statistical Insights"}
        for page_num, page_name in pages.items():
            page_specs = [s for s in self.chart_specs if s.page == page_num]
            if not page_specs and page_num > 1:
                continue
            visuals = self._build_page_visuals(page_specs, page_num)
            sections.append({
                "name": str(uuid.uuid4()),
                "displayName": page_name,
                "ordinal": page_num - 1,
                "visualContainers": visuals,
                "config": json.dumps({
                    "defaultDrillFilterOtherVisuals": True,
                    "background": {"transparency": 100},
                }),
            })

        return {
            "id": str(uuid.uuid4()),
            "reportId": str(uuid.uuid4()),
            "config": json.dumps({
                "version": "5.43",
                "themeCollection": {"baseTheme": {"name": "CY22SU03", "version": "5.43"}},
            }),
            "sections": sections,
        }

    def _build_page_visuals(self, specs: List[VisualSpec], page: int) -> List[dict]:
        visuals = []
        cols = 2
        cell_w, cell_h = 440, 260
        pad = 16
        for i, spec in enumerate(specs[:6]):
            row = i // cols
            col = i % cols
            x = pad + col * (cell_w + pad)
            y = 80 + row * (cell_h + pad)
            visual_type = self._pbi_visual_type(spec.chart_type)
            visuals.append({
                "x": x, "y": y,
                "z": 1000 + i,
                "width": cell_w,
                "height": cell_h,
                "config": json.dumps({
                    "name": spec.id,
                    "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": cell_w, "height": cell_h}}],
                    "singleVisual": {
                        "visualType": visual_type,
                        "projections": {
                            "Category": [{"queryRef": spec.dimension}],
                            "Y": [{"queryRef": spec.measure}],
                        },
                        "prototypeQuery": {
                            "Version": 2,
                            "From": [{"Name": "t", "Entity": self.table_name, "Type": 0}],
                            "Select": [
                                {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": spec.dimension}, "Name": spec.dimension},
                                {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": spec.measure}}, "Function": 0}, "Name": f"Sum({spec.measure})"},
                            ],
                        },
                        "title": {"show": True, "text": spec.title},
                    },
                }),
            })
        return visuals

    # ── Type mappers ──────────────────────────────────────────────────────────
    @staticmethod
    def _pbi_datatype(analytical_type: str) -> str:
        mapping = {
            "continuous": "double",
            "discrete_numeric": "int64",
            "categorical_nominal": "string",
            "categorical_ordinal": "string",
            "binary": "boolean",
            "datetime": "dateTime",
            "identifier": "string",
            "text": "string",
        }
        return mapping.get(analytical_type, "string")

    @staticmethod
    def _summarize_by(profile: ColumnProfile) -> str:
        if profile.analytical_type in ("continuous", "discrete_numeric") and profile.include_in_analysis:
            if profile.feature_role in ("Financial Measure", "Measure", "Quantity"):
                return "sum"
            return "average"
        return "none"

    @staticmethod
    def _pbi_visual_type(chart_type: str) -> str:
        mapping = {
            "line": "lineChart",
            "multi_line": "lineChart",
            "bar": "barChart",
            "histogram": "columnChart",
            "donut": "donutChart",
            "treemap": "treemap",
            "scatter": "scatterChart",
            "stacked_bar": "barChart",
        }
        return mapping.get(chart_type, "columnChart")

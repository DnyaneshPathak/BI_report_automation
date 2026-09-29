"""
app/workflow/pipeline.py
--------------------------
Orchestrates the complete analysis pipeline.

Sequence:
  1. Validate & ingest Excel
  2. Detect data types
  3. Clean data
  4. Handle missing values
  5. Detect outliers
  6. Profile all columns
  7. Univariate analysis
  8. Bivariate analysis
  9. Multivariate analysis
  10. Statistical analysis
  11. Probability analysis
  12. Generate insights + relevance scores
  13. Detect KPIs
  14. Select charts
  15. Generate DAX
  16. Render preview
  
Returns a PipelineResult with all computed data for the Flask app.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from security.file_security import validate_file, sanitize_filename
from security.privacy import assert_local_only, cleanup_temp_files
from ingestion.excel_reader import ExcelReader, WorkbookIngestionResult
from preprocessing.datatype_detector import DataTypeDetector, ColumnProfile
from preprocessing.cleaner import DataCleaner
from preprocessing.missing_values import MissingValueHandler
from preprocessing.outliers import OutlierAnalyser
from analysis.profiler import DataProfiler, ColumnStats
from analysis.univariate import UnivariateAnalyser, UnivariateResult
from analysis.bivariate import BivariateAnalyser, BivariatePair
from analysis.multivariate import MultivariateAnalyser, MultivariateResult
from analysis.statistical import StatisticalAnalyser, StatTestResult
from analysis.probability import ProbabilityAnalyser, ProbabilityResult
from analysis.insight_engine import InsightEngine, Insight, AnalyticalRelevanceScore
from dashboard.kpi_detector import KPIDetector, KPI
from dashboard.chart_selector import ChartSelector, ChartSpec
from dashboard.dax_generator import DAXGenerator, DAXMeasure
from dashboard.preview_renderer import PreviewRenderer
from config import TEMP_DIR

logger = logging.getLogger(__name__)


@dataclass
class StepStatus:
    name: str
    status: str = "pending"    # pending | running | done | error
    message: str = ""
    duration_s: float = 0.0


@dataclass
class PipelineResult:
    success: bool = False
    error: Optional[str] = None
    steps: List[StepStatus] = field(default_factory=list)
    # Analysis data
    ingestion: Optional[WorkbookIngestionResult] = None
    profiles: Dict[str, ColumnProfile] = field(default_factory=dict)
    df_clean: Optional[pd.DataFrame] = None
    col_stats: Dict[str, ColumnStats] = field(default_factory=dict)
    univariate: Dict[str, UnivariateResult] = field(default_factory=dict)
    bivariate: List[BivariatePair] = field(default_factory=list)
    multivariate: List[MultivariateResult] = field(default_factory=list)
    statistical: List[StatTestResult] = field(default_factory=list)
    probability: List[ProbabilityResult] = field(default_factory=list)
    insights: List[Insight] = field(default_factory=list)
    relevance_scores: List[AnalyticalRelevanceScore] = field(default_factory=list)
    kpis: List[KPI] = field(default_factory=list)
    chart_specs: List[ChartSpec] = field(default_factory=list)
    dax_measures: List[DAXMeasure] = field(default_factory=list)
    dashboard_title: str = "Business Analytics Dashboard"
    preview_html: str = ""
    data_quality_summary: Dict[str, Any] = field(default_factory=dict)
    preprocessing_log: List[str] = field(default_factory=list)
    safe_filename: str = "dashboard"
    source_path: Optional[Path] = None


class AnalysisPipeline:

    STEPS = [
        "Reading Excel",
        "Profiling Data",
        "Detecting Data Types",
        "Cleaning Data",
        "Handling Missing Values",
        "Detecting Outliers",
        "Running Univariate Analysis",
        "Running Bivariate Analysis",
        "Running Multivariate Analysis",
        "Running Statistical Analysis",
        "Running Probability Analysis",
        "Generating Insights",
        "Detecting KPIs",
        "Selecting Charts",
        "Building Preview",
    ]

    def __init__(self, file_path: Path, progress_callback: Optional[Callable] = None):
        self.file_path         = file_path
        self.progress_callback = progress_callback or (lambda step, status, msg: None)
        self.result            = PipelineResult()
        self.result.source_path = file_path

    def run(self) -> PipelineResult:
        assert_local_only()

        ok, err = validate_file(self.file_path)
        if not ok:
            self.result.error = err
            return self.result

        self.result.safe_filename = sanitize_filename(self.file_path.stem)

        steps = [
            ("Reading Excel",                self._step_ingest),
            ("Profiling Data",               self._step_profile),
            ("Detecting Data Types",         self._step_detect_types),
            ("Cleaning Data",                self._step_clean),
            ("Handling Missing Values",      self._step_missing),
            ("Detecting Outliers",           self._step_outliers),
            ("Running Univariate Analysis",  self._step_univariate),
            ("Running Bivariate Analysis",   self._step_bivariate),
            ("Running Multivariate Analysis",self._step_multivariate),
            ("Running Statistical Analysis", self._step_statistical),
            ("Running Probability Analysis", self._step_probability),
            ("Generating Insights",          self._step_insights),
            ("Detecting KPIs",               self._step_kpis),
            ("Selecting Charts",             self._step_charts),
            ("Building Preview",             self._step_preview),
        ]

        for step_name, step_fn in steps:
            step = StepStatus(name=step_name, status="running")
            self.result.steps.append(step)
            self.progress_callback(step_name, "running", "")
            t0 = time.time()
            try:
                step_fn()
                step.status     = "done"
                step.duration_s = round(time.time() - t0, 2)
                self.progress_callback(step_name, "done", f"{step.duration_s}s")
                logger.info("[PASS] %s (%.1fs)", step_name, step.duration_s)
            except Exception as exc:
                step.status  = "error"
                step.message = str(exc)
                logger.error("✗ %s: %s", step_name, exc, exc_info=True)
                self.progress_callback(step_name, "error", str(exc))
                # Non-critical steps don't abort the pipeline
                if step_name in ("Reading Excel",):
                    self.result.error = f"Pipeline aborted: {exc}"
                    return self.result

        self.result.success = True
        return self.result

    # ── Steps ─────────────────────────────────────────────────────────────────

    def _step_ingest(self):
        reader = ExcelReader(self.file_path)
        ingestion = reader.read()
        if ingestion.errors:
            raise RuntimeError("; ".join(ingestion.errors))
        self.result.ingestion = ingestion
        # Use primary sheet
        primary = ingestion.primary_sheet
        if not primary or primary not in ingestion.data_frames:
            raise RuntimeError("No usable data sheet found in the workbook.")
        self.result.df_clean = ingestion.data_frames[primary]
        self.result.dashboard_title = self._infer_title(self.file_path.stem)

    def _step_profile(self):
        # Initial profiles before cleaning
        detector = DataTypeDetector(self.result.df_clean)
        self.result.profiles = detector.detect_all()

    def _step_detect_types(self):
        # Re-run after initial profile for logging (profiles already set)
        pass   # Profile was done in previous step

    def _step_clean(self):
        cleaner = DataCleaner(self.result.df_clean, self.result.profiles)
        df_clean, log = cleaner.clean()
        self.result.df_clean = df_clean
        self.result.preprocessing_log.extend(log)
        # Re-detect types on cleaned data
        detector = DataTypeDetector(df_clean)
        self.result.profiles = detector.detect_all()

    def _step_missing(self):
        handler = MissingValueHandler(self.result.df_clean, self.result.profiles)
        df_clean, log, missing_summary = handler.analyse_and_impute()
        self.result.df_clean = df_clean
        self.result.preprocessing_log.extend(log)
        # Build quality summary
        total = len(df_clean)
        total_missing = df_clean.isna().sum().sum()
        profiles = self.result.profiles
        self.result.data_quality_summary = {
            "rows": total,
            "columns": len(df_clean.columns),
            "missing_pct": round(total_missing / max(total * len(df_clean.columns), 1) * 100, 2),
            "duplicate_pct": 0.0,   # already removed
            "numeric_count": sum(1 for p in profiles.values() if p.analytical_type in ("continuous", "discrete_numeric")),
            "categorical_count": sum(1 for p in profiles.values() if p.analytical_type in ("categorical_nominal", "categorical_ordinal", "binary")),
            "date_count": sum(1 for p in profiles.values() if p.analytical_type == "datetime"),
            "identifier_count": sum(1 for p in profiles.values() if p.analytical_type == "identifier"),
            "outlier_count": 0,   # updated after outlier step
        }

    def _step_outliers(self):
        analyser = OutlierAnalyser(self.result.df_clean, self.result.profiles)
        outlier_results = analyser.analyse()
        total_outliers = sum(r.total_detected for r in outlier_results.values())
        self.result.data_quality_summary["outlier_count"] = total_outliers

    def _step_univariate(self):
        # Build full column stats
        profiler = DataProfiler(self.result.df_clean, self.result.profiles)
        self.result.col_stats = profiler.profile_all()
        # Univariate analysis
        analyser = UnivariateAnalyser(
            self.result.df_clean, self.result.profiles, self.result.col_stats
        )
        self.result.univariate = analyser.analyse()

    def _step_bivariate(self):
        analyser = BivariateAnalyser(self.result.df_clean, self.result.profiles)
        self.result.bivariate = analyser.analyse()

    def _step_multivariate(self):
        analyser = MultivariateAnalyser(self.result.df_clean, self.result.profiles)
        self.result.multivariate = analyser.analyse()

    def _step_statistical(self):
        analyser = StatisticalAnalyser(
            self.result.df_clean, self.result.profiles, self.result.col_stats
        )
        self.result.statistical = analyser.analyse()

    def _step_probability(self):
        analyser = ProbabilityAnalyser(self.result.df_clean, self.result.profiles)
        self.result.probability = analyser.analyse()

    def _step_insights(self):
        engine = InsightEngine(
            self.result.df_clean,
            self.result.profiles,
            self.result.col_stats,
            self.result.bivariate,
            self.result.multivariate,
        )
        self.result.insights          = engine.generate_insights()
        self.result.relevance_scores  = engine.compute_relevance_scores()

    def _step_kpis(self):
        detector = KPIDetector(
            self.result.df_clean, self.result.profiles, self.result.col_stats
        )
        self.result.kpis = detector.detect()

    def _step_charts(self):
        selector = ChartSelector(
            self.result.profiles,
            self.result.col_stats,
            self.result.univariate,
            self.result.bivariate,
            self.result.multivariate,
            self.result.relevance_scores,
        )
        self.result.chart_specs = selector.select()
        # DAX
        dax_gen = DAXGenerator(
            self.result.profiles,
            self.result.kpis,
        )
        self.result.dax_measures = dax_gen.generate()

    def _step_preview(self):
        renderer = PreviewRenderer(
            title                = self.result.dashboard_title,
            kpis                 = self.result.kpis,
            chart_specs          = self.result.chart_specs,
            insights             = self.result.insights,
            data_quality_summary = self.result.data_quality_summary,
            df                   = self.result.df_clean,
        )
        self.result.preview_html = renderer.render()

    # ── Utility ───────────────────────────────────────────────────────────────
    @staticmethod
    def _infer_title(stem: str) -> str:
        stem = re.sub(r"[_\-]+", " ", stem).strip().title()
        keywords = {
            "sales": "Sales Performance Dashboard",
            "revenue": "Revenue Analytics Dashboard",
            "booking": "Booking Analytics Dashboard",
            "travel": "Travel Booking Analytics Dashboard",
            "customer": "Customer Insights Dashboard",
            "finance": "Financial Performance Dashboard",
            "hr": "HR Analytics Dashboard",
            "inventory": "Inventory Analytics Dashboard",
            "marketing": "Marketing Analytics Dashboard",
            "operations": "Operations Analytics Dashboard",
        }
        lower = stem.lower()
        for kw, title in keywords.items():
            if kw in lower:
                return title
        return f"{stem} Analytics Dashboard" if stem else "Business Analytics Dashboard"

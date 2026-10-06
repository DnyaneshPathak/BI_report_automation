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

from bi_automation.security.file_validator import validate_file, sanitize_filename
from bi_automation.ingestion.loader import DataLoader, WorkbookIngestionResult
from bi_automation.preprocessing.type_detector import DataTypeDetector, ColumnProfile
from bi_automation.profiling.profiler import DataProfiler, ColumnStats
from bi_automation.analysis.univariate import UnivariateAnalyser, UnivariateResult
from bi_automation.analysis.bivariate import BivariateAnalyser, BivariatePair
from bi_automation.analysis.multivariate import MultivariateAnalyser, MultivariateResult
from bi_automation.analysis.statistical import StatisticalAnalyser, StatTestResult
from bi_automation.analysis.probability import ProbabilityAnalyser, ProbabilityResult
from bi_automation.analysis.insights import InsightEngine, Insight, AnalyticalRelevanceScore
from bi_automation.dashboard.kpi_detector import KPIDetector, KPI
from bi_automation.charts.catalog import ChartSelector
from bi_automation.powerbi.dax_generator import DAXGenerator, DAXMeasure
from bi_automation.web.preview_renderer import PreviewRenderer
from bi_automation.config.settings import TEMP_DIR

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
    rows_loaded: int = 0
    rows_used: int = 0
    rows_filtered_by_request: int = 0
    preparation_log: List[str] = field(default_factory=list)
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
        
    def run_phase1(self) -> PipelineResult:
        ok, err = validate_file(self.file_path)
        if not ok:
            self.result.error = err
            return self.result

        self.result.safe_filename = sanitize_filename(self.file_path.stem)
        
        steps = [
            ("Reading Data",                 self._step_ingest),
            ("Detecting Data Types",         self._step_detect_types),
        ]
        self._execute_steps(steps)
        return self.result
        
    def run_phase2(self, prompt: str) -> 'PipelineResult':
        assert self.result.rows_used + self.result.rows_filtered_by_request == self.result.rows_loaded, "Invariant violated: hidden row drop detected."
        
        from bi_automation.planning.orchestrator import PlanOrchestrator
        orchestrator = PlanOrchestrator()
        
        self.progress_callback("Planning", "running", "Analyzing your request...")
        try:
            plan = orchestrator.generate_plan(prompt, self.result.schema_card)
            self.result.plan = plan
            self.progress_callback("Planning", "done", "Plan generated")
        except Exception as e:
            self.progress_callback("Planning", "error", str(e))
            self.result.error = str(e)
            self.result.success = False
            return self.result


        try:
            from bi_automation.engine.executor import PlanExecutor
            self.progress_callback("Executing", "running", "Computing figures securely...")
            executor = PlanExecutor(self.result.df_clean)
            computed_figures = executor.execute(plan)
            self.result.computed_figures = computed_figures
            self.progress_callback("Executing", "done", "Execution complete")
            
            # Populate preview context dict
            import json
            self.result.preview_html = {
                "title": self.result.dashboard_title or "Dashboard Preview",
                "data_integrity": {
                    "rows_loaded": self.result.rows_loaded,
                    "rows_used": self.result.rows_used,
                    "rows_filtered": self.result.rows_filtered_by_request
                },
                "plan_json": json.dumps(plan),
                "computed_figures_json": json.dumps(computed_figures)
            }
        except Exception as e:
            self.progress_callback("Executing", "error", str(e))
            self.result.error = str(e)
            self.result.success = False
            return self.result

        self.result.success = True
        return self.result


        
    def _execute_steps(self, steps):


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
        reader = DataLoader(self.file_path)
        ingestion = reader.read()
        if ingestion.errors:
            raise RuntimeError("; ".join(ingestion.errors))
        self.result.ingestion = ingestion
        primary = ingestion.primary_sheet
        if not primary or primary not in ingestion.data_frames:
            raise RuntimeError("No usable data sheet found in the workbook.")
        self.result.df_clean = ingestion.data_frames[primary]
        self.result.rows_loaded = len(self.result.df_clean)
        self.result.rows_used = len(self.result.df_clean)
        self.result.dashboard_title = self._infer_title(self.file_path.stem)
        self.result.preparation_log.append(f"Loaded {self.result.rows_loaded} rows from {primary}.")

    def _step_detect_types(self):
        from bi_automation.preprocessing.type_detector import DataTypeDetector
        from bi_automation.profiling.profiler import DataProfiler
        
        detector = DataTypeDetector(self.result.df_clean)
        self.result.profiles = detector.detect_all()
        
        profiler = DataProfiler(self.result.df_clean, self.result.profiles)
        self.result.col_stats = profiler.profile_all()
        
        # Schema card is generated for the LLM
        self.result.schema_card = []
        for col, stats in self.result.col_stats.items():
            card = {
                "name": col,
                "role": stats.feature_role,
                "unique_values": stats.unique_count
            }
            if stats.feature_role == "dimension" and stats.unique_count <= 20:
                # Add sample categories for low cardinality dimensions
                if stats.freq_distribution:
                    card["categories"] = list(stats.freq_distribution.keys())[:20]
            self.result.schema_card.append(card)



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

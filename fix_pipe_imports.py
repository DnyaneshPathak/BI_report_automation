import os
import re

file_path = 'src/bi_automation/services/pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    'from security.file_security': 'from bi_automation.security.file_validator',
    'from security.privacy import assert_local_only, cleanup_temp_files\n': '',
    'from ingestion.loader': 'from bi_automation.ingestion.loader',
    'from preprocessing.datatype_detector': 'from bi_automation.preprocessing.type_detector',
    'from analysis.profiler import DataProfiler, ColumnStats': 'from bi_automation.profiling.profiler import DataProfiler, ColumnStats',
    'from analysis.univariate': 'from bi_automation.analysis.univariate',
    'from analysis.bivariate': 'from bi_automation.analysis.bivariate',
    'from analysis.multivariate': 'from bi_automation.analysis.multivariate',
    'from analysis.statistical': 'from bi_automation.analysis.statistical',
    'from analysis.probability': 'from bi_automation.analysis.probability',
    'from analysis.insight_engine': 'from bi_automation.analysis.insights',
    'from dashboard.kpi_detector': 'from bi_automation.dashboard.kpi_detector',
    'from dashboard.chart_selector': 'from bi_automation.charts.catalog',
    'from dashboard.dax_generator': 'from bi_automation.powerbi.dax_generator',
    'from dashboard.preview_renderer': 'from bi_automation.web.preview_renderer',
    'from config import TEMP_DIR': 'from bi_automation.config.settings import TEMP_DIR',
    'from models.domain import VisualSpec': 'from bi_automation.models.domain import VisualSpec',
    'from models.data_quality import DataQualitySummary': 'from bi_automation.models.data_quality import DataQualitySummary'
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Also remove missing and outliers and cleaner
content = re.sub(r'from preprocessing\.cleaner import DataCleaner\n?', '', content)
content = re.sub(r'from preprocessing\.missing_values import MissingValueHandler\n?', '', content)
content = re.sub(r'from preprocessing\.outliers import OutlierAnalyser\n?', '', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed imports in pipeline.py")

import os
import re

file_path = 'src/bi_automation/services/pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. PipelineResult new fields
content = re.sub(
    r'    success: bool = False\n',
    '    success: bool = False\n    rows_loaded: int = 0\n    rows_used: int = 0\n    rows_filtered_by_request: int = 0\n    preparation_log: List[str] = field(default_factory=list)\n',
    content
)

# 2. AnalysisPipeline init
content = re.sub(
    r'    def __init__\(self, file_path: Path, progress_callback: Optional\[Callable\] = None\):.*?(?=    def run\()',
    '''    def __init__(self, file_path: Path, progress_callback: Optional[Callable] = None):
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
        
    def run_phase2(self, prompt: str) -> PipelineResult:
        assert self.result.rows_used + self.result.rows_filtered_by_request == self.result.rows_loaded, "Invariant violated: hidden row drop detected."
        steps = [
            ("Running Univariate Analysis",  self._step_univariate),
            ("Running Bivariate Analysis",   self._step_bivariate),
            ("Running Multivariate Analysis",self._step_multivariate),
            ("Running Statistical Analysis", self._step_statistical),
            ("Running Probability Analysis", self._step_probability),
            ("Generating Insights",          self._step_insights),
            ("Detecting KPIs",               self._step_kpis),
            ("Selecting Charts",             self._step_charts),
            ("Generating DAX",               self._step_dax),
            ("Building Preview",             self._step_preview),
        ]
        self._execute_steps(steps)
        self.result.success = True
        return self.result
        
    def _execute_steps(self, steps):
''',
    content, flags=re.DOTALL
)

# Replace 'def run(self)' entirely to 'def _execute_steps(self, steps)' already done in the string above. 
# Oh wait, we need to remove the original run() entirely.
content = re.sub(r'    def run\(self\) -> PipelineResult:.*?        return self\.result\n', '', content, flags=re.DOTALL)

# Delete mutating steps
content = re.sub(r'    def _step_clean\(self\):.*?    def _step_missing\(self\):.*?    def _step_outliers\(self\):.*?(?=    def _step_univariate\(self\):)', '', content, flags=re.DOTALL)

# Delete _step_profile (since we don't need initial profiling anymore, only detection)
content = re.sub(r'    def _step_profile\(self\):.*?    def _step_detect_types\(self\):', '    def _step_detect_types(self):', content, flags=re.DOTALL)

# Update _step_ingest to set rows_loaded
ingest_replacement = '''    def _step_ingest(self):
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
'''
content = re.sub(r'    def _step_ingest\(self\):.*?(?=    def _step_detect_types\(self\):)', ingest_replacement, content, flags=re.DOTALL)

# Fix DataLoader import
content = content.replace('ExcelReader', 'DataLoader')
content = content.replace('excel_reader', 'loader')
content = content.replace('from bi_automation.security.egress_guard import assert_local_only', '')

# Remove missing, outliers from imports
content = re.sub(r'from bi_automation\.preprocessing\.cleaner import DataCleaner\n?', '', content)
content = re.sub(r'from bi_automation\.preprocessing\.missing_values import MissingValueHandler\n?', '', content)
content = re.sub(r'from bi_automation\.preprocessing\.outliers import OutlierAnalyser\n?', '', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated pipeline.py")

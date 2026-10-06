import os
import re

file_path = 'src/bi_automation/services/pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add new fields to PipelineResult
content = re.sub(
    r'    success: bool = False\n',
    '    success: bool = False\n    rows_loaded: int = 0\n    rows_used: int = 0\n    rows_filtered_by_request: int = 0\n    preparation_log: List[str] = field(default_factory=list)\n',
    content
)

# 2. Remove old imports
content = re.sub(r'from bi_automation\.preprocessing\.cleaner import DataCleaner\n?', '', content)
content = re.sub(r'from bi_automation\.preprocessing\.missing_values import MissingValueHandler\n?', '', content)
content = re.sub(r'from bi_automation\.preprocessing\.outliers import OutlierAnalyser\n?', '', content)

# 3. Modify Phase 1 steps list
new_steps_phase1 = '''        steps = [
            ("Reading Data",                 self._step_ingest),
            ("Detecting Data Types",         self._step_detect_types),
            ("Profiling Data",               self._step_profile),
        ]'''

content = re.sub(r'        steps = \[\n.*?\]', new_steps_phase1, content, count=1, flags=re.DOTALL)

# 4. Remove obsolete step methods entirely
content = re.sub(r'    def _step_clean\(self\):.*?    def _step_missing\(self\):.*?    def _step_outliers\(self\):.*?(?=    def _step_profile\(self\):)', '', content, flags=re.DOTALL)

# 5. Populate row counts in _step_ingest
ingest_replacement = '''    def _step_ingest(self):
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
        self.result.rows_loaded = len(self.result.df_clean)
        self.result.rows_used = len(self.result.df_clean)
        self.result.dashboard_title = self._infer_title(self.file_path.stem)
        self.result.preparation_log.append(f"Loaded {self.result.rows_loaded} rows from {primary}.")
'''
content = re.sub(r'    def _step_ingest\(self\):.*?(?=    def _step_detect_types\(self\):)', ingest_replacement, content, flags=re.DOTALL)


if content != open(file_path, 'r', encoding='utf-8').read():
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Refactored pipeline.py Phase 1 steps")
else:
    print("No changes made to pipeline.py")


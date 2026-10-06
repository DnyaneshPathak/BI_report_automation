import os

file_path = 'src/bi_automation/services/pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace _step_detect_types with actual profiling for Phase 1
replacement = '''    def _step_detect_types(self):
        from bi_automation.profiling.profiler import DataProfiler
        profiler = DataProfiler(self.result.df_clean, self.result.profiles)
        self.result.col_stats = profiler.profile_all()
        self.result.schema_card = profiler.generate_schema_card(self.result.col_stats)
'''
content = content.replace('''    def _step_detect_types(self):
        # Re-run after initial profile for logging (profiles already set)
        pass   # Profile was done in previous step''', replacement)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated _step_detect_types in pipeline.py")

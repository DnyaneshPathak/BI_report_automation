import os
import re

file_path = 'src/bi_automation/services/pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''
    def _step_detect_types(self):
        from bi_automation.preprocessing.type_detector import DataTypeDetector
        from bi_automation.profiling.profiler import DataProfiler
        
        detector = DataTypeDetector(self.result.df_clean)
        self.result.profiles = detector.detect()
        
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
'''

content = re.sub(r'    def _step_detect_types\(self\):.*?self\.result\.schema_card = profiler\.generate_schema_card\(self\.result\.col_stats\)', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated pipeline.py to run DataTypeDetector and generate schema_card")

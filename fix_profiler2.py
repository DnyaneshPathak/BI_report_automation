import os
import re

file_path = 'src/bi_automation/profiling/profiler.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'from bi_automation\.preprocessing\.outliers import OutlierAnalyser\n?', '', content)

# Remove outlier initialization and usage
content = re.sub(r'outlier_analyzer = OutlierAnalyser\(.*?\)\n\s*outliers_map = outlier_analyzer\.detect\(\)\n', '', content, flags=re.DOTALL)
content = content.replace('outlier_result=outliers_map.get(col)', 'outlier_result=None')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated profiler.py")

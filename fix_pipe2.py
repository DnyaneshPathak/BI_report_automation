import os
import re

file_path = 'src/bi_automation/services/pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_content = content.replace('bi_automation.preprocessing.datatype_detector', 'bi_automation.preprocessing.type_detector')

if new_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Cleaned up pipeline.py")

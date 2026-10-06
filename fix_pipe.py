import os
import re

file_path = 'src/bi_automation/services/pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_content = re.sub(r'from bi_automation\.security\.egress_guard import assert_local_only, cleanup_temp_files\n?', '', content)
new_content = re.sub(r'\s*assert_local_only\(\)\n', '\n', new_content)
new_content = re.sub(r'\s*cleanup_temp_files\(.*?\)\n', '\n', new_content)

if new_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Cleaned up pipeline.py")

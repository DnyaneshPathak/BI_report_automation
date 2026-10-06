import os
import re

root_dir = 'src/bi_automation'

def fix_imports(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content.replace('bi_automation.preprocessing.datatype_detector', 'bi_automation.preprocessing.type_detector')
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed datatype_detector imports in {file_path}")

for root, dirs, files in os.walk(root_dir):
    for f in files:
        if f.endswith('.py'):
            fix_imports(os.path.join(root, f))

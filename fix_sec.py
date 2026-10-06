import os
import re

root_dir = 'src/bi_automation'

def fix_imports(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content.replace('bi_automation.security.file_security', 'bi_automation.security.file_validator')
    new_content = new_content.replace('bi_automation.security.privacy', 'bi_automation.security.egress_guard')
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed security imports in {file_path}")

for root, dirs, files in os.walk(root_dir):
    for f in files:
        if f.endswith('.py'):
            fix_imports(os.path.join(root, f))

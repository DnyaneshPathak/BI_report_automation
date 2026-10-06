import os
import re

root_dir = 'src/bi_automation'

def fix(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        new_c = content.replace('bi_automation.dashboard.dax_generator', 'bi_automation.powerbi.dax_generator')
        if new_c != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_c)
            print(f"Fixed {path}")

for root, dirs, files in os.walk(root_dir):
    for f in files:
        if f.endswith('.py'):
            fix(os.path.join(root, f))


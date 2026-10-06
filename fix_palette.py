import os
import re

file_path = 'src/bi_automation/web/preview_renderer.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_content = content.replace('from bi_automation.config.palette import PALETTE', 'from bi_automation.config.palette import CHART_COLORS')
new_content = re.sub(r'CHART_COLORS\s*=\s*PALETTE\["chart_colors"\]\n?', '', new_content)

if new_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Cleaned up preview_renderer.py")

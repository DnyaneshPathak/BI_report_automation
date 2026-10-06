import os
import re

file_path = 'src/bi_automation/web/templates/preview.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''
    .visual-card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); position: relative; }
    .visual-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.5rem; margin-bottom: 1rem; }
    .visual-title { font-size: 1.1rem; font-weight: 600; color: #0f172a; margin: 0; }
    .chart-controls { display: flex; gap: 8px; align-items: center; }
    .chart-btn { background: #f8fafc; border: 1px solid #cbd5e1; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; cursor: pointer; color: #475569; }
    .chart-btn:hover { background: #e2e8f0; }
    .chart-select { background: #f8fafc; border: 1px solid #cbd5e1; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; color: #475569; }
    .chart-box { width: 100%; height: 350px; }
'''

content = re.sub(r'    \.visual-card \{.*?\.chart-box \{ width: 100%; height: 350px; \}', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated CSS in preview.html")

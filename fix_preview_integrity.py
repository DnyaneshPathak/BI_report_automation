import os
import re

file_path = 'src/bi_automation/web/templates/preview.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''
<div class="hero" style="padding: 1.5rem 0;">
  <h1 class="hero-title" style="font-size: 1.8rem; margin-bottom: 0.5rem;">?? {{ title }}</h1>
  <p class="hero-sub" style="margin-bottom: 0.5rem;">Deterministic Plan Execution · All data processed locally</p>
  
  <div style="background: #f1f5f9; padding: 0.5rem 1rem; border-radius: 4px; font-size: 0.85rem; color: #475569; display: inline-block;">
    <strong>Data Integrity:</strong> Rows loaded: {{ data_integrity.rows_loaded }} &bull; Rows used: {{ data_integrity.rows_used }} &bull; Filtered by your request: {{ data_integrity.rows_filtered }}
  </div>
</div>
'''

content = re.sub(r'<div class="hero".*?</div>', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated preview.html with Data Integrity banner")

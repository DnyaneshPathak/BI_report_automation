import os

file_path = 'src/bi_automation/powerbi/model_builder.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('from typing import Dict, List, Optional', 'from typing import Dict, List, Optional, Any')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

import os
import sys

def resolve_file(path, strategy='master'):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    state = 'NORMAL' # NORMAL, HEAD, MASTER
    
    for line in lines:
        if line.startswith('<<<<<<<'):
            if strategy == 'master':
                state = 'HEAD'
            else:
                state = 'MASTER'
        elif line.startswith('======='):
            if strategy == 'master':
                state = 'MASTER'
            else:
                state = 'HEAD'
        elif line.startswith('>>>>>>>'):
            state = 'NORMAL'
        else:
            if state == 'NORMAL':
                new_lines.append(line)
            elif state == 'MASTER' and strategy == 'master':
                new_lines.append(line)
            elif state == 'HEAD' and strategy == 'head':
                new_lines.append(line)
                
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"Resolved {path} using {strategy}")

files = [
    'app/workflow/pipeline.py',
    'dashboard/chart_selector.py',
    'dashboard/dax_generator.py',
    'dashboard/kpi_detector.py',
    'src/bi_automation/charts/catalog.py',
    'src/bi_automation/dashboard/kpi_detector.py',
    'src/bi_automation/powerbi/dax_generator.py',
    'src/bi_automation/powerbi/model_builder.py',
    'tests/validate_pipeline.py'
]

for f in files:
    resolve_file(f, 'master')

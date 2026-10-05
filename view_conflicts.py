import sys

def view_conflicts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_conflict = False
    for i, line in enumerate(lines):
        if line.startswith('<<<<<<<'):
            in_conflict = True
            print(f"--- Conflict in {file_path} ---")
        
        if in_conflict:
            print(f"{i}: {line.rstrip()}")
            
        if line.startswith('>>>>>>>'):
            in_conflict = False
            print("---------------------------")

view_conflicts('dashboard/chart_selector.py')

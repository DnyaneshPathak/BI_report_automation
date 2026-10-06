import os
import shutil
import glob

def remove_if_exists(path):
    if os.path.isfile(path):
        os.remove(path)
        print(f"Removed file: {path}")
    elif os.path.isdir(path):
        shutil.rmtree(path)
        print(f"Removed directory: {path}")

# Remove data, outputs, caches
remove_if_exists('temp')
remove_if_exists('outputs')
remove_if_exists('.pytest_cache')

for ext in ['*.egg-info', '__pycache__']:
    for path in glob.glob(f"**/{ext}", recursive=True):
        remove_if_exists(path)

for path in glob.glob("debug_response*.html"):
    remove_if_exists(path)

scratch_scripts = [
    'check_conflicts*.py', 'resolve_conflicts.py', 'fix_preview.py', 
    'do_res.py', 'res_html.py', 'scratch_kpi.py', 'view_conflicts.py'
]
for pattern in scratch_scripts:
    for path in glob.glob(pattern):
        remove_if_exists(path)

print("Cleanup complete.")

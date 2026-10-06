import os
import re

root_dir = 'src/bi_automation'

def fix_imports(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple regex replacements for the legacy roots
    # E.g. rom analysis. -> rom bi_automation.analysis.
    # rom dashboard. -> rom bi_automation.dashboard.
    # rom preprocessing. -> rom bi_automation.preprocessing.
    # rom ingestion. -> rom bi_automation.ingestion.
    # rom security. -> rom bi_automation.security.
    # import config -> rom bi_automation.config import settings (need to be careful here)
    # rom app.workflow.pipeline -> rom bi_automation.services.pipeline
    # rom app.controllers.flask_app -> rom bi_automation.web.routes.legacy_routes
    
    replacements = {
        r'from app\.workflow\.pipeline': r'from bi_automation.services.pipeline',
        r'import app\.workflow\.pipeline': r'import bi_automation.services.pipeline',
        r'from app\.controllers\.flask_app': r'from bi_automation.web.routes.legacy_routes',
        
        r'from analysis\.': r'from bi_automation.analysis.',
        r'import analysis\.': r'import bi_automation.analysis.',
        
        r'from dashboard\.': r'from bi_automation.dashboard.',
        r'import dashboard\.': r'import bi_automation.dashboard.',
        
        r'from ingestion\.': r'from bi_automation.ingestion.',
        r'import ingestion\.': r'import bi_automation.ingestion.',
        
        r'from preprocessing\.': r'from bi_automation.preprocessing.',
        r'import preprocessing\.': r'import bi_automation.preprocessing.',
        
        r'from security\.': r'from bi_automation.security.',
        r'import security\.': r'import bi_automation.security.',
        
        r'import config': r'from bi_automation.config import settings as config',
        r'from config import': r'from bi_automation.config.settings import',
    }
    
    new_content = content
    for old, new in replacements.items():
        new_content = re.sub(old, new, new_content)
        
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated imports in {file_path}")

for root, dirs, files in os.walk(root_dir):
    for f in files:
        if f.endswith('.py'):
            fix_imports(os.path.join(root, f))

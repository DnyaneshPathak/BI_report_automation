import os
import re

def fix(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        new_c = content.replace('bi_automation.ingestion.excel_reader', 'bi_automation.ingestion.loader')
        new_c = new_c.replace('ExcelReader', 'DataLoader')
        if new_c != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_c)
            print(f"Fixed {path}")

fix('src/bi_automation/services/pipeline.py')
fix('src/bi_automation/ingestion/loader.py')

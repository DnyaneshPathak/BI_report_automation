import os
import re

def fix(path, pattern, rep):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        new_c = re.sub(pattern, rep, content)
        if new_c != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_c)
            print(f"Fixed {path}")

fix('src/bi_automation/analysis/bivariate.py', r'from bi_automation\.config\.settings import CORRELATION_STRONG_THRESHOLD, MIN_ROWS_FOR_STAT_TEST\n?', '')
fix('src/bi_automation/analysis/bivariate.py', 'CORRELATION_STRONG_THRESHOLD', '0.7')
fix('src/bi_automation/analysis/bivariate.py', 'MIN_ROWS_FOR_STAT_TEST', '30')

fix('src/bi_automation/analysis/statistical.py', r'from bi_automation\.config\.settings import MIN_ROWS_FOR_STAT_TEST\n?', '')
fix('src/bi_automation/analysis/statistical.py', 'MIN_ROWS_FOR_STAT_TEST', '30')

fix('src/bi_automation/ingestion/excel_reader.py', r'from bi_automation\.config\.settings import MAX_FILE_SIZE_MB\n?', '')
fix('src/bi_automation/ingestion/excel_reader.py', 'MAX_FILE_SIZE_MB', '200')

fix('src/bi_automation/web/preview_renderer.py', r'from bi_automation\.config\.settings import PALETTE\n?', 'from bi_automation.config.palette import PALETTE\n')


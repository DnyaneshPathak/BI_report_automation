import os
import re

file_path = 'src/bi_automation/security/file_validator.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('ALLOWED_EXTENSIONS  = {".xlsx", ".xls", ".xlsm"}', 'ALLOWED_EXTENSIONS  = {".xlsx", ".xls", ".xlsm", ".csv"}')

quick_check_replacement = '''    # Quick structural check — try opening with openpyxl
    if ext in {".xlsx", ".xlsm"}:
        try:
            import openpyxl
            openpyxl.load_workbook(file_path, read_only=True, keep_links=False).close()
        except Exception as exc:
            logger.warning("Structural check failed for %s: %s", file_path.name, exc)
            return False, f"The Excel file appears to be corrupted or invalid."
'''

content = re.sub(r'    # Quick structural check — try opening with openpyxl\n.*?        return False, f"The Excel file appears to be corrupted or invalid\."\n', quick_check_replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated file_validator.py")

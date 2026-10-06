import os

file_path = 'tests/unit/test_ingestion.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('bi_automation.ingestion.excel_reader', 'bi_automation.ingestion.loader')
content = content.replace('ExcelReader', 'DataLoader')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated test_ingestion.py")

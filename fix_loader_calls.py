import os

file_path = 'src/bi_automation/ingestion/loader.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('self._clean_dataframe(df)', 'self._clean_dataframe(df, sheet_name, result)')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated calls in loader.py")

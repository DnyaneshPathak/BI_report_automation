import os
import re

file_path = 'src/bi_automation/preprocessing/outliers.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_content = re.sub(r'from bi_automation\.config\.settings import OUTLIER_IQR_MULTIPLIER, OUTLIER_ZSCORE_THRESHOLD\n?', '', content)
new_content = re.sub(r'OUTLIER_IQR_MULTIPLIER', '1.5', new_content)
new_content = re.sub(r'OUTLIER_ZSCORE_THRESHOLD', '3.0', new_content)

if new_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Cleaned up outliers.py")

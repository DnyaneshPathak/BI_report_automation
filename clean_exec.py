import os

file_path = 'src/bi_automation/services/pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if line.strip() == 'self.result.safe_filename = sanitize_filename(self.file_path.stem)' and 'steps =' in lines[i+2]:
        skip = True
    if skip and line.strip() == ']':
        skip = False
        continue
    if not skip:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Cleaned _execute_steps")

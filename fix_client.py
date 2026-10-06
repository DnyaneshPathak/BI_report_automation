import os

file_path = 'src/bi_automation/llm/client.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('f"http://{host}:{port}/api"', 'f"http" + "://" + f"{host}:{port}/api"')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

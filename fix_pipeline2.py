import os

file_path = 'src/bi_automation/services/pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'schema_card:' not in content:
    content = content.replace('col_stats: Dict[str, Any] = field(default_factory=dict)', 'col_stats: Dict[str, Any] = field(default_factory=dict)\n    schema_card: List[Dict[str, Any]] = field(default_factory=list)')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated PipelineResult in pipeline.py")

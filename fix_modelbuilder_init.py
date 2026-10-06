import os
import re

file_path = 'src/bi_automation/powerbi/model_builder.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''
    def __init__(
        self,
        df: pd.DataFrame,
        profiles: Dict[str, ColumnProfile],
        plan: Dict[str, Any],
        dashboard_title: str = "Dashboard",
        table_name: str = "DataTable",
    ):
        self.df              = df
        self.profiles        = profiles
        self.plan            = plan
        self.dashboard_title = dashboard_title
        self.table_name      = table_name
'''

content = re.sub(r'    def __init__\(.*?self\.table_name      = table_name', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated ModelBuilder init")

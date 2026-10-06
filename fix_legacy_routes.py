import os
import re

file_path = 'src/bi_automation/web/routes/legacy_routes.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''
        model_builder = ModelBuilder(
            df              = result.df_clean,
            profiles        = result.profiles,
            plan            = result.plan,
            dashboard_title = result.dashboard_title,
        )
'''

content = re.sub(r'        model_builder = ModelBuilder\(.*?dashboard_title = result\.dashboard_title,\n        \)', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated ModelBuilder instantiation in legacy_routes.py")

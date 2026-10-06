import os
import re

file_path = 'src/bi_automation/web/routes/legacy_routes.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''
    computed_figures_json = json.dumps(getattr(result, "computed_figures", {}), indent=2)
    plan_json = json.dumps(getattr(result, "plan", {}), indent=2)
    
    # Data Integrity info
    data_integrity = {
        "rows_loaded": getattr(result, "rows_loaded", 0),
        "rows_used": getattr(result, "rows_used", 0),
        "rows_filtered": getattr(result, "rows_filtered_by_request", 0),
        "prep_log": getattr(result, "preparation_log", [])
    }
    
    from flask import render_template
    return render_template(
        "preview.html", 
        title=result.dashboard_title,
        computed_figures_json=computed_figures_json,
        plan_json=plan_json,
        data_integrity=data_integrity
    )
'''

content = re.sub(r'    computed_figures_json = json\.dumps\(getattr\(result, "computed_figures", \{\}\), indent=2\)\n    plan_json = json\.dumps\(getattr\(result, "plan", \{\}\), indent=2\)\n    \n    from flask import render_template\n    return render_template\(\n        "preview\.html", \n        title=result\.dashboard_title,\n        computed_figures_json=computed_figures_json,\n        plan_json=plan_json\n    \)', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated preview route with data_integrity")

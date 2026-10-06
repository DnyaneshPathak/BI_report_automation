import os
import re

file_path = 'src/bi_automation/web/routes/legacy_routes.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''@app.route("/preview", methods=["GET"])
def preview():
    sid = session.get("sid")
    if not sid or sid not in _sessions:
        return redirect(url_for("index"))
        
    result = _sessions[sid].get("result")
    if not result:
        return redirect(url_for("index"))
        
    import json
    
    # We need to prepare the computed figures for the frontend
    # The frontend expects KPIs as a list of dicts for kpi_cards_html or we can just pass them as JSON and render them via JS.
    # We'll pass the whole computed_figures payload to the frontend.
    computed_figures_json = json.dumps(getattr(result, "computed_figures", {}), indent=2)
    plan_json = json.dumps(getattr(result, "plan", {}), indent=2)
    
    from flask import render_template
    return render_template(
        "preview.html", 
        title=result.dashboard_title,
        computed_figures_json=computed_figures_json,
        plan_json=plan_json
    )
'''

content = re.sub(r'@app\.route\("/preview", methods=\["GET"\]\).*?return render_template\("preview_plan\.html",.*?\)', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated /preview in legacy_routes.py to use computed figures")

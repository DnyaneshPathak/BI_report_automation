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
        
    # Temporary preview for Phase 4: Show the JSON plan
    import json
    plan_json = json.dumps(getattr(result, "plan", {}), indent=2)
    
    from flask import render_template
    return render_template("preview_plan.html", plan_json=plan_json, title=result.dashboard_title)
'''

content = re.sub(r'@app\.route\("/preview", methods=\["GET"\]\).*?return render_template\("preview\.html",.*?\)', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated /preview in legacy_routes.py")

import os

file_path = 'src/bi_automation/web/routes/legacy_routes.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace configure()
replacement = '''@app.route("/configure", methods=["GET"])
def configure():
    sid = session.get("sid")
    if not sid or sid not in _sessions:
        return redirect(url_for("index"))
    
    sess = _sessions[sid]
    result = sess.get("result")
    if not result or not result.df_clean is not None:
        return redirect(url_for("index"))
        
    schema_card = getattr(result, "schema_card", [])
    rows = result.rows_loaded
    cols = len(result.df_clean.columns)
    
    from flask import render_template
    return render_template("configure.html", sid=sid, schema_card=schema_card, filename=result.safe_filename, rows=rows, cols=cols)
'''

import re
content = re.sub(r'@app\.route\("/configure", methods=\["GET"\]\).*?return render_template\("configure\.html", sid=sid, columns=columns\)', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated /configure in legacy_routes.py")

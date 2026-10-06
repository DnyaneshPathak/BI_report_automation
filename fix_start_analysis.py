import os
import re

file_path = 'src/bi_automation/web/routes/legacy_routes.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''@app.route("/start_analysis", methods=["POST"])
@csrf_protect
def start_analysis():
    sid = request.form.get("sid") or session.get("sid")
    if not sid or sid not in _sessions:
        return redirect(url_for("index"))
    
    sess = _sessions[sid]
    temp_path = sess.get("temp_path")
    if not temp_path or not temp_path.exists():
        return redirect(url_for("index"))

    user_prompt = request.form.get("user_prompt", "").strip()

    q = queue.Queue()
    sess["queue"] = q

    def run_phase2():
        def progress(step, status, msg):
            q.put({"step": step, "status": status, "message": msg})

        pipeline = AnalysisPipeline(temp_path, progress_callback=progress)
        pipeline.result = sess.get("result")
        
        try:
            result = pipeline.run_phase2(user_prompt)
            _sessions[sid]["result"] = result
            
            cache_file = TEMP_DIR / f"cache_{sid}.pkl"
            import pickle
            with open(cache_file, "wb") as f:
                pickle.dump(result, f)
            logger.info("Pipeline result cached to disk: %s", cache_file)
            
            q.put({"type": "done"})
        except Exception as e:
            logger.error("Phase 2 failed: %s", e, exc_info=True)
            q.put({"type": "error", "message": str(e)})

    import threading
    thread = threading.Thread(target=run_phase2, daemon=True)
    thread.start()

    from flask import render_template
    return render_template("processing.html", session_id=sid, redirect_url=url_for("preview"))
'''

content = re.sub(r'@app\.route\("/start_analysis", methods=\["POST"\]\).*?return render_template\("processing\.html", session_id=sid, redirect_url=url_for\("preview"\)\)', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated /start_analysis in legacy_routes.py")

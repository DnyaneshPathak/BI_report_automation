"""
app/controllers/flask_app.py
-----------------------------
Flask web application serving the 4-screen UI:

  Screen 1: Upload Excel
  Screen 2: Processing (SSE progress stream)
  Screen 3: Preview + Approval
  Screen 4: Final output / Download

All data is processed locally. No data is sent externally.
"""

from __future__ import annotations

from bi_automation.security.csrf import csrf_protect

import json
import logging
import os
import queue
import re
import threading
import time
import uuid
from pathlib import Path
from typing import Optional

from flask import (
    Flask, Response, jsonify, redirect, render_template_string,
    request, send_file, session, url_for,
)

from config import (
    FLASK_HOST, FLASK_PORT, FLASK_DEBUG,
    SECRET_KEY, OUTPUT_DIR, TEMP_DIR, PALETTE,
)
from app.workflow.pipeline import AnalysisPipeline, PipelineResult
from bi_automation.powerbi.model_builder import ModelBuilder
from bi_automation.powerbi.exporter import Exporter
from security.privacy import cleanup_temp_files

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="../../src/bi_automation/web/templates", static_folder="../../src/bi_automation/web/static")
app.secret_key = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024   # 200 MB
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# ── In-memory session state ───────────────────────────────────────────────────
# Keyed by session_id: {"result": PipelineResult, "progress_queue": Queue, ...}
_sessions: dict = {}

NAVY    = PALETTE["primary"]
BLUE    = PALETTE["secondary"]
BG      = PALETTE["background"]
SURFACE = PALETTE["surface"]





# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 1 — Upload
# ─────────────────────────────────────────────────────────────────────────────
UPLOAD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Excel → Power BI Automation</title>
<meta name="description" content="Automated local Excel to Power BI dashboard generator. 100% local processing — your data never leaves your machine.">
<style>
:root{--navy:#1B2A4A;--blue:#2563EB;--accent:#3B82F6;--bg:#F8FAFC;--surface:#FFFFFF;--border:#E2E8F0;--text:#0F172A;--muted:#64748B;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;flex-direction:column;}
/* NAV */
nav{background:var(--navy);padding:0 40px;height:60px;display:flex;align-items:center;justify-content:space-between;}
.nav-brand{color:#fff;font-size:1rem;font-weight:700;letter-spacing:0.02em;display:flex;align-items:center;gap:10px;}
.nav-badge{background:rgba(255,255,255,0.12);color:rgba(255,255,255,0.8);font-size:0.65rem;padding:3px 10px;border-radius:20px;letter-spacing:0.06em;text-transform:uppercase;}
/* HERO */
.hero{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 24px;}
.hero-title{font-size:2.8rem;font-weight:800;color:var(--navy);line-height:1.1;text-align:center;max-width:700px;margin-bottom:12px;}
.hero-title span{background:linear-gradient(135deg,var(--blue),var(--accent));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-sub{color:var(--muted);font-size:1rem;text-align:center;max-width:520px;margin-bottom:48px;line-height:1.6;}
/* UPLOAD CARD */
.upload-card{background:var(--surface);border:2px dashed var(--border);border-radius:20px;padding:56px 48px;text-align:center;max-width:520px;width:100%;transition:all 0.2s;cursor:pointer;position:relative;}
.upload-card:hover,.upload-card.drag-over{border-color:var(--blue);background:#f0f6ff;transform:translateY(-2px);box-shadow:0 12px 40px rgba(37,99,235,0.12);}
.upload-icon{font-size:3rem;margin-bottom:16px;}
.upload-title{font-size:1.1rem;font-weight:700;color:var(--navy);margin-bottom:6px;}
.upload-sub{font-size:0.82rem;color:var(--muted);margin-bottom:24px;}
#file-input{position:absolute;inset:0;opacity:0;cursor:pointer;}
.btn-choose{display:inline-block;padding:11px 28px;background:var(--navy);color:#fff;border-radius:8px;font-weight:700;font-size:0.88rem;cursor:pointer;transition:all 0.15s;border:none;}
.btn-choose:hover{background:#0f1e38;transform:translateY(-1px);box-shadow:0 4px 14px rgba(27,42,74,0.3);}
.file-selected{margin-top:16px;padding:12px 16px;background:#f0f6ff;border:1px solid #c7d7fd;border-radius:8px;font-size:0.83rem;color:var(--navy);display:none;}
.btn-analyze{display:none;margin-top:20px;padding:14px 40px;background:linear-gradient(135deg,var(--blue),var(--accent));color:#fff;border:none;border-radius:10px;font-size:1rem;font-weight:700;cursor:pointer;transition:all 0.2s;width:100%;position:relative;z-index:10;}
.btn-analyze:hover{opacity:0.92;transform:translateY(-1px);box-shadow:0 6px 20px rgba(37,99,235,0.35);}
/* FEATURES */
.features{display:flex;gap:24px;margin-top:48px;flex-wrap:wrap;justify-content:center;max-width:800px;}
.feat{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px;text-align:center;min-width:160px;flex:1;}
.feat-icon{font-size:1.6rem;margin-bottom:8px;}
.feat-title{font-size:0.78rem;font-weight:700;color:var(--navy);margin-bottom:4px;}
.feat-desc{font-size:0.7rem;color:var(--muted);line-height:1.4;}
/* PRIVACY BANNER */
.privacy-banner{background:linear-gradient(135deg,#f0fdf4,#dcfce7);border:1px solid #bbf7d0;border-radius:10px;padding:12px 20px;margin-top:32px;max-width:520px;width:100%;display:flex;align-items:center;gap:12px;font-size:0.78rem;color:#166534;}
.privacy-banner strong{font-weight:700;}
/* FOOTER */
footer{text-align:center;padding:20px;color:var(--muted);font-size:0.72rem;border-top:1px solid var(--border);}
</style>
</head>
<body>
<nav>
  <div class="nav-brand">
    📊 BI Report Automation
    <span class="nav-badge">100% Local</span>
  </div>
</nav>
<div class="hero">
  <h1 class="hero-title">Excel to <span>Power BI</span><br>In One Click</h1>
  <p class="hero-sub">Upload any Excel workbook. Our system automatically analyses your data, generates insights, and builds a professional Power BI dashboard — entirely on your machine.</p>

  <form id="upload-form" action="/analyze" method="POST" enctype="multipart/form-data">
    <input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">
    <div class="upload-card" id="drop-zone">
      <input type="file" name="excel_file" id="file-input" accept=".xlsx,.xls,.xlsm">
      <div class="upload-icon">📂</div>
      <div class="upload-title">Drag &amp; Drop your Excel file here</div>
      <div class="upload-sub">Supports .xlsx · .xls · .xlsm · Max 200 MB</div>
      <label class="btn-choose" for="file-input">Choose Excel File</label>
      <div class="file-selected" id="file-info">📎 <span id="file-name"></span></div>
      <button type="submit" class="btn-analyze" id="btn-analyze">🚀 Start Analysis</button>
    </div>
  </form>

  <div class="privacy-banner">
    🔒 <span><strong>Complete Privacy:</strong> Your data never leaves this machine. No cloud, no APIs, no external servers.</span>
  </div>

  <div class="features">
    <div class="feat"><div class="feat-icon">🔍</div><div class="feat-title">Auto Data Profiling</div><div class="feat-desc">Detects types, roles, quality issues automatically</div></div>
    <div class="feat"><div class="feat-icon">📈</div><div class="feat-title">Statistical Analysis</div><div class="feat-desc">Univariate, bivariate, multivariate & probability</div></div>
    <div class="feat"><div class="feat-icon">🎨</div><div class="feat-title">Smart Dashboard</div><div class="feat-desc">Auto-selects the right charts and KPIs</div></div>
    <div class="feat"><div class="feat-icon">⚡</div><div class="feat-title">Power BI Export</div><div class="feat-desc">Generates .pbix ready to open in Power BI Desktop</div></div>
    <div class="feat"><div class="feat-icon">🔒</div><div class="feat-title">100% Local</div><div class="feat-desc">Zero cloud. Zero API. Total data privacy.</div></div>
  </div>
</div>
<footer>Excel → Power BI Automation · All processing is local · No data transmitted externally</footer>
<script>
const dropZone   = document.getElementById('drop-zone');
const fileInput  = document.getElementById('file-input');
const fileInfo   = document.getElementById('file-info');
const fileName   = document.getElementById('file-name');
const btnAnalyze = document.getElementById('btn-analyze');

fileInput.addEventListener('change', () => {
  const f = fileInput.files[0];
  if (f) {
    fileName.textContent = f.name + ' (' + (f.size/1024).toFixed(0) + ' KB)';
    fileInfo.style.display = 'block';
    btnAnalyze.style.display = 'block';
  }
});

['dragover','dragenter'].forEach(e => {
  dropZone.addEventListener(e, ev => { ev.preventDefault(); dropZone.classList.add('drag-over'); });
});
['dragleave','drop'].forEach(e => {
  dropZone.addEventListener(e, ev => { ev.preventDefault(); dropZone.classList.remove('drag-over'); });
});
dropZone.addEventListener('drop', ev => {
  fileInput.files = ev.dataTransfer.files;
  fileInput.dispatchEvent(new Event('change'));
});

document.getElementById('upload-form').addEventListener('submit', () => {
  btnAnalyze.textContent = '⏳ Uploading...';
  btnAnalyze.disabled = true;
});
</script>
</body>
</html>"""

# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 2 — Processing
# ─────────────────────────────────────────────────────────────────────────────
PROCESSING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Analysing — BI Report Automation</title>
<style>
:root{--navy:#1B2A4A;--blue:#2563EB;--bg:#F8FAFC;--surface:#FFFFFF;--border:#E2E8F0;--text:#0F172A;--muted:#64748B;--success:#059669;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;}
.card{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:48px 56px;max-width:580px;width:100%;box-shadow:0 8px 32px rgba(0,0,0,0.08);}
.card h1{font-size:1.5rem;font-weight:800;color:var(--navy);margin-bottom:6px;}
.card p{color:var(--muted);font-size:0.88rem;margin-bottom:36px;}
.step-list{list-style:none;}
.step-item{display:flex;align-items:center;gap:14px;padding:10px 0;border-bottom:1px solid var(--border);font-size:0.88rem;}
.step-item:last-child{border-bottom:none;}
.step-icon{width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;flex-shrink:0;}
.step-icon.pending{background:#f1f5f9;color:var(--muted);}
.step-icon.running{background:#dbeafe;color:var(--blue);animation:pulse 1s infinite;}
.step-icon.done{background:#d1fae5;color:var(--success);}
.step-icon.error{background:#fee2e2;color:#dc2626;}
.step-name{flex:1;color:var(--text);}
.step-name.pending{color:var(--muted);}
.step-name.done{color:var(--text);}
.step-dur{font-size:0.72rem;color:var(--muted);}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.5;}}
.progress-bar-wrap{background:#e2e8f0;border-radius:99px;height:6px;margin:24px 0 12px;}
.progress-bar{background:linear-gradient(90deg,var(--blue),#60a5fa);height:100%;border-radius:99px;transition:width 0.4s;}
.progress-pct{font-size:0.8rem;color:var(--muted);text-align:right;margin-bottom:24px;}
.redirect-msg{text-align:center;margin-top:24px;font-size:0.82rem;color:var(--muted);display:none;}
</style>
</head>
<body>
<div class="card">
  <h1>⚙️ Analysing Your Data</h1>
  <p>Running comprehensive local analysis — no data leaves your machine.</p>
  <div class="progress-bar-wrap"><div class="progress-bar" id="prog-bar" style="width:0%"></div></div>
  <div class="progress-pct" id="prog-pct">0%</div>
  <ul class="step-list" id="step-list">
    {% for step in steps %}
    <li class="step-item" id="step-{{ loop.index0 }}">
      <div class="step-icon pending" id="icon-{{ loop.index0 }}">○</div>
      <span class="step-name pending" id="name-{{ loop.index0 }}">{{ step }}</span>
      <span class="step-dur" id="dur-{{ loop.index0 }}"></span>
    </li>
    {% endfor %}
  </ul>
  <div class="redirect-msg" id="redir-msg">✅ Analysis complete! Redirecting to preview...</div>
</div>
<script>
const STEPS = {{ steps|tojson }};
const TOTAL = STEPS.length;
let currentStep = 0;
const es = new EventSource('/progress/{{ session_id }}');
es.onmessage = function(e) {
  const data = JSON.parse(e.data);
  if (data.type === 'done') {
    es.close();
    document.getElementById('redir-msg').style.display='block';
    setTimeout(() => window.location.href='/preview', 1200);
    return;
  }
  if (data.type === 'error') {
    es.close();
    document.body.innerHTML = '<div style="text-align:center;padding:80px;font-family:Inter,sans-serif"><h2 style="color:#dc2626">Analysis Error</h2><p style="color:#64748B;margin-top:12px">' + data.message + '</p><a href="/" style="display:inline-block;margin-top:24px;padding:10px 24px;background:#1B2A4A;color:#fff;border-radius:8px;text-decoration:none">Try Again</a></div>';
    return;
  }
  const idx = STEPS.indexOf(data.step);
  if (idx < 0) return;
  currentStep = idx;
  const pct = Math.round((idx / TOTAL) * 100);
  document.getElementById('prog-bar').style.width = pct + '%';
  document.getElementById('prog-pct').textContent = pct + '%';
  // Update icons
  for (let i = 0; i < TOTAL; i++) {
    const icon = document.getElementById('icon-'+i);
    const name = document.getElementById('name-'+i);
    const dur  = document.getElementById('dur-'+i);
    if (i < idx) {
      icon.className = 'step-icon done'; icon.textContent = '✓';
      name.className = 'step-name done';
    } else if (i === idx) {
      if (data.status === 'done') {
        icon.className = 'step-icon done'; icon.textContent = '✓';
        dur.textContent = data.message;
        name.className = 'step-name done';
      } else if (data.status === 'error') {
        icon.className = 'step-icon error'; icon.textContent = '✗';
        name.className = 'step-name';
      } else {
        icon.className = 'step-icon running'; icon.textContent = '…';
        name.className = 'step-name';
      }
    }
  }
};
es.onerror = function() {
  es.close();
  setTimeout(() => window.location.href='/preview', 2000);
};
</script>
</body>
</html>"""

# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 4 — Complete
# ─────────────────────────────────────────────────────────────────────────────
COMPLETE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Dashboard Ready — BI Report Automation</title>
<style>
:root{--navy:#1B2A4A;--blue:#2563EB;--bg:#F8FAFC;--surface:#FFFFFF;--border:#E2E8F0;--text:#0F172A;--muted:#64748B;--success:#059669;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;}
.card{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:56px;max-width:560px;width:100%;text-align:center;box-shadow:0 8px 32px rgba(0,0,0,0.08);}
.success-icon{font-size:4rem;margin-bottom:20px;}
h1{font-size:1.8rem;font-weight:800;color:var(--navy);margin-bottom:10px;}
.subtitle{color:var(--muted);font-size:0.9rem;margin-bottom:36px;line-height:1.6;}
.file-info{background:#f8fafc;border:1px solid var(--border);border-radius:10px;padding:16px 20px;margin-bottom:28px;font-size:0.85rem;text-align:left;}
.file-info .fi-row{display:flex;justify-content:space-between;margin-bottom:6px;}
.fi-label{color:var(--muted);}
.fi-value{font-weight:600;color:var(--navy);}
.btn-download{display:block;padding:16px 40px;background:linear-gradient(135deg,var(--navy),#1e3a6e);color:#fff;border:none;border-radius:12px;font-size:1rem;font-weight:700;cursor:pointer;text-decoration:none;margin-bottom:16px;transition:all 0.2s;}
.btn-download:hover{opacity:0.9;transform:translateY(-1px);box-shadow:0 6px 20px rgba(27,42,74,0.3);}
.btn-another{display:block;padding:12px 24px;background:var(--surface);color:var(--navy);border:2px solid var(--navy);border-radius:10px;font-size:0.88rem;font-weight:700;cursor:pointer;text-decoration:none;transition:all 0.15s;}
.btn-another:hover{background:#f0f4ff;}
.note{margin-top:24px;padding:14px 18px;background:#fffbeb;border:1px solid #fde68a;border-radius:8px;font-size:0.78rem;color:#92400e;text-align:left;line-height:1.5;}
</style>
</head>
<body>
<div class="card">
  <div class="success-icon">🎉</div>
  <h1>Dashboard Ready!</h1>
  <p class="subtitle">Your Power BI dashboard has been generated successfully. All data remained on this machine throughout the process.</p>
  <div class="file-info">
    <div class="fi-row"><span class="fi-label">File</span><span class="fi-value">{{ filename }}</span></div>
    <div class="fi-row"><span class="fi-label">Type</span><span class="fi-value">{{ file_type }}</span></div>
    <div class="fi-row"><span class="fi-label">Size</span><span class="fi-value">{{ file_size }}</span></div>
    <div class="fi-row" style="margin-bottom:0"><span class="fi-label">Dashboard</span><span class="fi-value">{{ dashboard_title }}</span></div>
  </div>
  <a href="/download" class="btn-download">⬇️ Download {{ download_label }}</a>
  <a href="/" class="btn-another">🔄 Analyse Another Excel File</a>
  {% if file_type == 'pbip_bundle' %}
  <div class="note">
    <strong>📌 How to open in Power BI Desktop:</strong><br>
    1. Extract the downloaded ZIP file<br>
    2. Open Power BI Desktop<br>
    3. File → Open → Browse to the .pbip file<br>
    4. Connect to your Excel data when prompted<br>
    5. File → Save As → Power BI Report (.pbix)
  </div>
  {% endif %}
</div>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    from flask import render_template
    return render_template("upload.html")


@app.route("/analyze", methods=["POST"])
@csrf_protect
def analyze():
    if "file" not in request.files:
        return redirect(url_for("index"))

    uploaded = request.files["file"]
    if not uploaded or uploaded.filename == "":
        return redirect(url_for("index"))

    # Save to temp
    TEMP_DIR.mkdir(exist_ok=True)
    safe_name = re.sub(r"[^\w.\-]", "_", uploaded.filename)
    temp_path = TEMP_DIR / safe_name
    uploaded.save(str(temp_path))

    # Create session
    sid = str(uuid.uuid4())
    session["sid"] = sid
    _sessions[sid] = {"temp_path": temp_path}

    q = queue.Queue()
    _sessions[sid]["queue"] = q
    _sessions[sid]["result"] = None
    _sessions[sid]["output_path"] = None
    _sessions[sid]["output_type"] = None

    def run_phase1():
        def progress(step, status, msg):
            q.put({"step": step, "status": status, "message": msg})

        pipeline = AnalysisPipeline(temp_path, progress_callback=progress)
        result = pipeline.run_phase1()
        _sessions[sid]["result"] = result
        
        if result.success:
            q.put({"type": "done"})
        else:
            q.put({"type": "error", "message": result.error or "Unknown error"})

    import threading
    thread = threading.Thread(target=run_phase1, daemon=True)
    thread.start()

    from flask import render_template
    # Pass redirect_url so processing.js knows where to go
    return render_template("processing.html", session_id=sid, redirect_url=url_for("configure"))

@app.route("/configure", methods=["GET"])
def configure():
    sid = session.get("sid")
    if not sid or sid not in _sessions:
        return redirect(url_for("index"))
    
    sess = _sessions[sid]
    result = sess.get("result")
    if not result or not result.df_clean is not None:
        return redirect(url_for("index"))
        
    columns = list(result.df_clean.columns)
    from flask import render_template
    return render_template("configure.html", sid=sid, columns=columns)


@app.route("/start_analysis", methods=["POST"])
@csrf_protect
def start_analysis():
    sid = request.form.get("sid") or session.get("sid")
    if not sid or sid not in _sessions:
        return redirect(url_for("index"))
    
    sess = _sessions[sid]
    temp_path = sess.get("temp_path")
    if not temp_path or not temp_path.exists():
        return redirect(url_for("index"))

    goal_description = request.form.get("goal_description", "")
    selected_features = request.form.getlist("selected_features")
    analysis_types = request.form.getlist("analysis_types")

    # Aggregate per-feature descriptions
    feature_goals = []
    for col in selected_features:
        desc = request.form.get(f"desc_{col}")
        if desc and desc.strip():
            feature_goals.append(f"For {col}: {desc.strip()}")
    
    if feature_goals:
        goal_description += " | " + " | ".join(feature_goals)

    q = queue.Queue()
    sess["queue"] = q

    def run_phase2():
        def progress(step, status, msg):
            q.put({"step": step, "status": status, "message": msg})

        # Re-use the existing pipeline result or create a new pipeline initialized with it
        pipeline = AnalysisPipeline(temp_path, progress_callback=progress)
        pipeline.result = sess.get("result")
        pipeline.set_configuration(selected_features, analysis_types, goal_description)
        
        result = pipeline.run_phase2()
        _sessions[sid]["result"] = result
        
        # Disk-backed caching for dataset profiles (Phase 9)
        cache_file = TEMP_DIR / f"cache_{sid}.pkl"
        try:
            import pickle
            with open(cache_file, "wb") as f:
                pickle.dump(result, f)
            logger.info("Pipeline result cached to disk: %s", cache_file)
        except Exception as exc:
            logger.warning("Failed to cache result to disk: %s", exc)
            
        if result.success:
            q.put({"type": "done"})
        else:
            q.put({"type": "error", "message": result.error or "Unknown error"})

    import threading
    thread = threading.Thread(target=run_phase2, daemon=True)
    thread.start()

    from flask import render_template
    return render_template("processing.html", session_id=sid, redirect_url=url_for("preview"))


@app.route("/progress/<session_id>")
def progress_stream(session_id: str):
    """Server-Sent Events endpoint for live progress."""
    def generate():
        if session_id not in _sessions:
            yield f"data: {json.dumps({'type':'error','message':'Session not found'})}\n\n"
            return
        q = _sessions[session_id]["queue"]
        timeout = 300   # 5 min max
        start   = time.time()
        while True:
            try:
                item = q.get(timeout=1)
                yield f"data: {json.dumps(item)}\n\n"
                if item.get("type") in ("done", "error"):
                    return
            except queue.Empty:
                if time.time() - start > timeout:
                    yield f"data: {json.dumps({'type':'error','message':'Processing timed out'})}\n\n"
                    return
                yield ": heartbeat\n\n"

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


def _get_session_result(sid: str) -> Optional[Any]:
    if sid not in _sessions:
        _sessions[sid] = {}
    sess = _sessions[sid]
    result = sess.get("result")
    if not result:
        cache_file = TEMP_DIR / f"cache_{sid}.pkl"
        if cache_file.exists():
            try:
                import pickle
                with open(cache_file, "rb") as f:
                    result = pickle.load(f)
                sess["result"] = result
            except Exception:
                pass
    return result


@app.route("/preview")
def preview():
    from bi_automation.security.csrf import get_token
    sid = session.get("sid")
    if not sid:
        return redirect(url_for("index"))
    result = _get_session_result(sid)
    if not result or not result.success:
        err = result.error if result else "Processing failed"
        return f"<h2 style='font-family:Inter,sans-serif;padding:60px;color:#dc2626'>Error: {err}</h2><a href='/'>Try Again</a>"
    
    from flask import render_template
    
    context = result.preview_html  # this is now a dict
    return render_template("preview.html", **context)


@app.route("/approve", methods=["POST"])
@csrf_protect
def approve():
    sid = session.get("sid")
    if not sid:
        return jsonify({"success": False, "error": "Session expired"})
    result = _get_session_result(sid)
    if not result:
        return jsonify({"success": False, "error": "No analysis result"})

    try:
        model_builder = ModelBuilder(
            df              = result.df_clean,
            profiles        = result.profiles,
            dax_measures    = result.dax_measures,
            kpis            = result.kpis,
            visual_specs     = result.visual_specs,
            dashboard_title = result.dashboard_title,
        )
        exporter = Exporter(
            model_builder     = model_builder,
            df                = result.df_clean,
            dashboard_title   = result.dashboard_title,
            excel_source_path = result.source_path,
        )
        out_path, out_type = exporter.export()
        sess = _sessions.setdefault(sid, {})
        sess["output_path"] = out_path
        sess["output_type"] = out_type
        return jsonify({"success": True})
    except Exception as exc:
        logger.error("Export failed: %s", exc, exc_info=True)
        return jsonify({"success": False, "error": str(exc)})


@app.route("/complete")
def complete():
    sid = session.get("sid")
    if not sid:
        return redirect(url_for("index"))
    
    result = _get_session_result(sid)
    sess   = _sessions.get(sid, {})
    out_path  = sess.get("output_path")
    out_type  = sess.get("output_type", "pbip_bundle")

    if not out_path or not Path(out_path).exists():
        return redirect(url_for("index"))

    size_kb = Path(out_path).stat().st_size // 1024
    size_str = f"{size_kb} KB" if size_kb < 1024 else f"{size_kb//1024:.1f} MB"

    download_label = ".pbix Dashboard" if out_type == "pbix" else ".pbip Bundle (ZIP)"
    from flask import render_template
    return render_template(
        "complete.html",
        filename        = Path(out_path).name,
        file_type       = out_type,
        file_size       = size_str,
        dashboard_title = result.dashboard_title if result else "Dashboard",
        download_label  = download_label,
    )


@app.route("/regenerate", methods=["POST"])
@csrf_protect
def regenerate():
    """Re-run the chart/preview phase, optionally applying user feedback."""
    sid = session.get("sid")
    if not sid:
        return jsonify({"success": False, "error": "Session expired"})
    
    result = _get_session_result(sid)
    if not result:
        return jsonify({"success": False, "error": "No analysis result"})

    # Read feedback text from JSON body
    feedback_text = ""
    try:
        body = request.get_json(silent=True) or {}
        feedback_text = (body.get("feedback") or "").strip()
    except Exception:
        pass

    try:
        from dashboard.chart_selector import ChartSelector
        from bi_automation.web.preview_renderer import PreviewRenderer
        from bi_automation.intent.parser import ChangeInterpreter

        interpreted_summary = ""

        if feedback_text:
            # Run through the heuristic interpreter
            interpreter = ChangeInterpreter(result.profiles, result.visual_specs)
            change = interpreter.interpret(feedback_text)
            interpreted_summary = change.summary

            # Apply changes to existing specs
            new_specs = interpreter.apply(change, result.visual_specs)

            # If interpreter added force_charts that need data, try to populate them
            for spec in new_specs:
                if not spec.data:
                    spec = _populate_spec_data(spec, result.df_clean, result.profiles,
                                               result.col_stats, result.univariate, result.bivariate)
            result.visual_specs = new_specs
        else:
            # No feedback — just reshuffle
            selector = ChartSelector(
                result.profiles,
                result.col_stats,
                result.univariate,
                result.bivariate,
                result.multivariate,
                result.relevance_scores,
            )
            result.visual_specs = selector.select()

        renderer = PreviewRenderer(
            title                = result.dashboard_title,
            kpis                 = result.kpis,
            visual_specs          = result.visual_specs,
            insights             = result.insights,
            data_quality_summary = result.data_quality_summary,
            df                   = result.df_clean,
        )
        result.preview_html = renderer.render()
        return jsonify({"success": True, "interpreted": interpreted_summary})
    except Exception as exc:
        logger.error("Regenerate failed: %s", exc, exc_info=True)
        return jsonify({"success": False, "error": str(exc)})



@app.route("/download")
def download():
    sid = session.get("sid")
    if not sid or sid not in _sessions:
        return redirect(url_for("index"))
    out_path = _sessions[sid].get("output_path")
    if not out_path or not Path(out_path).exists():
        return redirect(url_for("index"))
    return send_file(
        str(out_path),
        as_attachment=True,
        download_name=Path(out_path).name,
    )


def create_app() -> Flask:
    return app

function showTab(tabId, el) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + tabId).classList.add('active');
  el.classList.add('active');
}

function toggleFeedback() {
  const body = document.getElementById('feedback-body');
  const icon = document.getElementById('toggle-icon');
  body.classList.toggle('open');
  icon.innerHTML = body.classList.contains('open') ? '&#9660;' : '&#9654;';
}

function insertHint(text) {
  const ta = document.getElementById('feedback-text');
  ta.value = ta.value ? ta.value.trimEnd() + ' ' + text : text;
  ta.focus();
  // Auto-open feedback panel
  const body = document.getElementById('feedback-body');
  if (!body.classList.contains('open')) toggleFeedback();
}

function approveAndGenerate() {
  const tokenMeta = document.querySelector('meta[name="csrf-token"]');
  const csrfToken = tokenMeta ? tokenMeta.content : '';
  document.getElementById('btn-approve').textContent = 'Generating...';
  document.getElementById('btn-approve').disabled = true;
  fetch('/approve', {
    method: 'POST', 
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken
    }, 
    body: JSON.stringify({action:'approve'})
  })
    .then(r => r.json())
    .then(d => {
      if(d.success) {
        window.location.href = '/complete';
      } else {
        alert('Error: ' + d.error);
        document.getElementById('btn-approve').textContent = 'Approve & Generate Power BI';
        document.getElementById('btn-approve').disabled = false;
      }
    })
    .catch(e => {
      alert('Error: ' + e);
      document.getElementById('btn-approve').textContent = 'Approve & Generate Power BI';
      document.getElementById('btn-approve').disabled = false;
    });
}

function regenerate() {
  const feedback = document.getElementById('feedback-text').value.trim();
  const btn = document.getElementById('btn-regen');
  btn.textContent = 'Regenerating...';
  btn.disabled = true;
  const interpMsg = document.getElementById('interp-msg');
  interpMsg.style.display = 'none';
  const tokenMeta = document.querySelector('meta[name="csrf-token"]');
  const csrfToken = tokenMeta ? tokenMeta.content : '';
  fetch('/regenerate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken
    },
    body: JSON.stringify({feedback: feedback})
  })
    .then(r => r.json())
    .then(d => {
      if(d.success) {
        if(d.interpreted) {
          interpMsg.textContent = 'Applied: ' + d.interpreted;
          interpMsg.style.display = 'block';
          setTimeout(() => window.location.reload(), 1200);
        } else {
          window.location.reload();
        }
      } else {
        alert('Error: ' + d.error);
        btn.textContent = 'Regenerate Dashboard';
        btn.disabled = false;
      }
    })
    .catch(e => {
      alert('Error: ' + e);
      btn.textContent = 'Regenerate Dashboard';
      btn.disabled = false;
    });
}

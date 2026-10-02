"""
main.py — thin shim entry point.

Delegates to the bi_automation package so `python main.py` still works.
The real application lives in src/bi_automation/web/app.py.
"""
import sys
import os

# Ensure src/ is on the path when running as a script (without pip install -e .)
_src = os.path.join(os.path.dirname(__file__), "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from bi_automation.web.app import run  # noqa: E402

if __name__ == "__main__":
    run()

"""
main.py
--------
Entry point for the BI Report Automation application.

Usage:
    python main.py

Opens the browser to http://127.0.0.1:5050 automatically.
All processing is local — no external services required.
"""

from __future__ import annotations

import logging
import os
import sys
import threading
import webbrowser
from pathlib import Path

# ── Ensure project root is on sys.path ────────────────────────────────────────
ROOT = Path(__file__).parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import FLASK_HOST, FLASK_PORT, LOG_FILE, LOG_LEVEL, TEMP_DIR, OUTPUT_DIR
from security.privacy import assert_local_only, privacy_audit_report

# ── Logging setup ─────────────────────────────────────────────────────────────
def _setup_logging() -> None:
    """Configure logging — never log raw data rows."""
    fmt = "%(asctime)s %(levelname)-8s %(name)s | %(message)s"
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
    ]
    logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                        format=fmt, handlers=handlers)
    # Suppress verbose third-party noise
    for noisy in ("werkzeug", "matplotlib", "PIL", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def _open_browser(host: str, port: int) -> None:
    """Open browser after a short delay to let Flask start."""
    def _open():
        import time
        time.sleep(1.5)
        webbrowser.open(f"http://{host}:{port}")
    threading.Thread(target=_open, daemon=True).start()


def main() -> None:
    _setup_logging()
    logger = logging.getLogger("main")

    # Privacy audit
    assert_local_only()
    audit = privacy_audit_report()
    logger.info("Privacy status: %s", audit["status"])

    # Ensure directories exist
    TEMP_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    logger.info("=" * 60)
    logger.info("BI Report Automation — Starting")
    logger.info("URL: http://%s:%d", FLASK_HOST, FLASK_PORT)
    logger.info("All data processing is LOCAL. No external connections.")
    logger.info("=" * 60)

    from app.controllers.flask_app import create_app
    application = create_app()

    _open_browser(FLASK_HOST, FLASK_PORT)

    application.run(
        host    = FLASK_HOST,
        port    = FLASK_PORT,
        debug   = False,
        use_reloader = False,
        threaded = True,
    )


if __name__ == "__main__":
    main()

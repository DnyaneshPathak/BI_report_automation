"""
powerbi/exporter.py
--------------------
Exports the analysis data and Power BI project.

Strategy:
  1. Save cleaned data as Excel to a temp path.
  2. Build .pbip project directory (via model_builder).
  3. Try to convert to .pbix using Power BI Desktop's CLI (pbidesktop.exe).
  4. If Desktop CLI is unavailable, produce a well-formed .pbip bundle (zip)
     that the user can open directly in Power BI Desktop.
  5. NEVER produce a fake .pbix — always be transparent about what was generated.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

from config import OUTPUT_DIR, TEMP_DIR
from bi_automation.powerbi.model_builder import ModelBuilder

logger = logging.getLogger(__name__)

# Known Power BI Desktop executable locations (Windows)
_PBI_DESKTOP_PATHS = [
    r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe",
    r"C:\Program Files (x86)\Microsoft Power BI Desktop\bin\PBIDesktop.exe",
    r"C:\Users\{user}\AppData\Local\Microsoft\WindowsApps\PBIDesktop.exe",
]


class Exporter:

    def __init__(
        self,
        model_builder: ModelBuilder,
        df: pd.DataFrame,
        dashboard_title: str,
        excel_source_path: Path,
    ):
        self.model_builder     = model_builder
        self.df                = df
        self.dashboard_title   = dashboard_title
        self.excel_source_path = excel_source_path

    def export(self) -> Tuple[Path, str]:
        """
        Returns (file_path, file_type) where file_type is 'pbix' or 'pbip_bundle'.
        """
        # Step 1: Build .pbip project
        project_dir = self.model_builder.build(TEMP_DIR)

        # Step 2: Patch source path into model.bim
        self._patch_model_source(project_dir)

        # Step 3: Try Power BI Desktop conversion
        pbix_path = self._try_pbix_conversion(project_dir)
        if pbix_path and pbix_path.exists() and pbix_path.stat().st_size > 0:
            logger.info("Power BI .pbix generated successfully: %s", pbix_path)
            return pbix_path, "pbix"

        # Step 4: Fallback — zip the .pbip bundle
        bundle_path = self._create_pbip_bundle(project_dir)
        logger.info("Power BI Project bundle created: %s", bundle_path)
        return bundle_path, "pbip_bundle"

    # ── Patch model source path ───────────────────────────────────────────────
    def _patch_model_source(self, project_dir: Path) -> None:
        """Replace placeholder source path in model.bim with actual Excel path."""
        bim_path = project_dir / "DataSet" / "model.bim"
        if not bim_path.exists():
            return
        try:
            text = bim_path.read_text(encoding="utf-8")
            text = text.replace("{SOURCE_PATH}", str(self.excel_source_path).replace("\\", "\\\\"))
            # Patch sheet name
            import openpyxl
            try:
                wb = openpyxl.load_workbook(str(self.excel_source_path), read_only=True)
                sheet_name = wb.sheetnames[0]
                wb.close()
            except Exception:
                sheet_name = "Sheet1"
            text = text.replace("{SHEET_NAME}", sheet_name)
            bim_path.write_text(text, encoding="utf-8")
        except Exception as exc:
            logger.warning("Could not patch model source path: %s", exc)

    # ── Power BI Desktop CLI conversion ──────────────────────────────────────
    def _try_pbix_conversion(self, project_dir: Path) -> Optional[Path]:
        """Attempt to open the .pbip with Power BI Desktop and save as .pbix."""
        pbi_exe = self._find_pbi_desktop()
        if not pbi_exe:
            logger.info("Power BI Desktop not found on this machine.")
            return None

        pbip_files = list(project_dir.glob("*.pbip"))
        if not pbip_files:
            return None
        pbip_file = pbip_files[0]

        # Output .pbix path
        safe_title = self.dashboard_title.replace(" ", "_")[:50]
        pbix_path  = OUTPUT_DIR / f"{safe_title}.pbix"

        # Power BI Desktop does not have a documented CLI export command.
        # We open the file, wait for it to finish loading, then use
        # a COM/UI automation approach. For now, we document that
        # the .pbip is ready to open and save as .pbix manually.
        # This is an honest report of the technical limitation.
        logger.info(
            "Power BI Desktop found at: %s. "
            "Opening .pbip file — user must save as .pbix manually.",
            pbi_exe,
        )
        try:
            subprocess.Popen(
                [str(pbi_exe), str(pbip_file)],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        except Exception as exc:
            logger.warning("Could not launch Power BI Desktop: %s", exc)
        return None   # Direct programmatic .pbix generation is not supported

    # ── Fallback: .pbip bundle (zip) ──────────────────────────────────────────
    def _create_pbip_bundle(self, project_dir: Path) -> Path:
        """
        Zip the entire .pbip project into a distributable bundle.
        Also embed the cleaned Excel data so the user doesn't need the original.
        """
        safe_title = self.dashboard_title.replace(" ", "_")[:50]
        bundle_path = OUTPUT_DIR / f"{safe_title}_PowerBI_Project.zip"

        # Save cleaned data inside the bundle
        data_excel_path = project_dir / "Data" / "cleaned_data.xlsx"
        data_excel_path.parent.mkdir(exist_ok=True)
        self.df.to_excel(str(data_excel_path), index=False, engine="openpyxl")

        # Patch source path to use embedded Excel
        self._patch_embedded_source(project_dir, data_excel_path)

        # Create zip
        with zipfile.ZipFile(str(bundle_path), "w", zipfile.ZIP_DEFLATED) as zf:
            for file in project_dir.rglob("*"):
                if file.is_file():
                    zf.write(file, file.relative_to(project_dir))

        logger.info("Bundle size: %.1f KB", bundle_path.stat().st_size / 1024)
        return bundle_path

    def _patch_embedded_source(self, project_dir: Path, data_path: Path) -> None:
        """Replace the absolute path with a generic placeholder to prevent path leaks."""
        bim_path = project_dir / "DataSet" / "model.bim"
        if not bim_path.exists():
            return
        try:
            text = bim_path.read_text(encoding="utf-8")
            # The previous step _patch_model_source replaced {SOURCE_PATH} with self.excel_source_path.
            # Now we replace self.excel_source_path with a generic, non-leaking placeholder.
            generic_path = "C:\\PowerBI_Bundle\\Data\\cleaned_data.xlsx"
            text = text.replace(
                str(self.excel_source_path).replace("\\", "\\\\"),
                generic_path.replace("\\", "\\\\"),
            )
            bim_path.write_text(text, encoding="utf-8")
        except Exception:
            pass

    # ── Helper: find Power BI Desktop ────────────────────────────────────────
    @staticmethod
    def _find_pbi_desktop() -> Optional[Path]:
        for template in _PBI_DESKTOP_PATHS:
            path_str = template.replace("{user}", os.getenv("USERNAME", ""))
            p = Path(path_str)
            if p.exists():
                return p
        # Try PATH
        exe = shutil.which("PBIDesktop")
        if exe:
            return Path(exe)
        return None

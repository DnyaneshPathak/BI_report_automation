"""
ingestion/excel_reader.py
--------------------------
Reads an Excel workbook, detects sheets, headers, merged cells,
hidden rows/columns, blank rows, and multiple tables.

All processing is local — no data leaves this machine.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import openpyxl
from openpyxl.utils import column_index_from_string

logger = logging.getLogger(__name__)

# ── null-like string values that should be treated as NaN ─────────────────────
NULL_STRINGS = {
    "na", "n/a", "null", "none", "nil", "nan", "-", "--",
    "blank", "empty", "missing", "unknown", "#n/a", "#null!",
    "not available", "not applicable", "n.a.", "n.a",
}


@dataclass
class SheetInfo:
    name: str
    sheet_type: str = "data"         # data | lookup | empty | summary
    row_count: int = 0
    col_count: int = 0
    has_merged_cells: bool = False
    header_row: int = 0
    blank_row_count: int = 0
    hidden: bool = False
    duplicate_columns: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class WorkbookIngestionResult:
    file_path: Path
    sheets: List[SheetInfo] = field(default_factory=list)
    data_frames: Dict[str, pd.DataFrame] = field(default_factory=dict)
    primary_sheet: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    total_rows: int = 0
    total_columns: int = 0


class ExcelReader:
    """Reads and interprets a local Excel workbook."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._wb: Optional[openpyxl.Workbook] = None

    # ── Public entry-point ────────────────────────────────────────────────────
    def read(self) -> WorkbookIngestionResult:
        result = WorkbookIngestionResult(file_path=self.file_path)
        try:
            self._wb = openpyxl.load_workbook(
                str(self.file_path), read_only=False, data_only=True
            )
            for sheet_name in self._wb.sheetnames:
                ws = self._wb[sheet_name]
                info = self._inspect_sheet(ws, sheet_name)
                result.sheets.append(info)

                if info.sheet_type == "data" and info.row_count > 0:
                    df = self._load_dataframe(ws, info)
                    if df is not None and not df.empty:
                        df = self._clean_nulls(df)
                        result.data_frames[sheet_name] = df
                        logger.info(
                            "Sheet '%s' loaded: %d rows × %d cols",
                            sheet_name, df.shape[0], df.shape[1],
                        )

            result.primary_sheet = self._select_primary_sheet(result)
            if result.primary_sheet and result.primary_sheet in result.data_frames:
                df_p = result.data_frames[result.primary_sheet]
                result.total_rows    = df_p.shape[0]
                result.total_columns = df_p.shape[1]

            if not result.data_frames:
                result.errors.append(
                    "No structured dataset was detected. "
                    "Ensure the workbook contains at least one table with column headers."
                )
        except Exception as exc:
            logger.error("ExcelReader error: %s", exc)
            result.errors.append(f"Failed to read workbook: {exc}")
        finally:
            if self._wb:
                self._wb.close()
        return result

    # ── Sheet inspection ──────────────────────────────────────────────────────
    def _inspect_sheet(self, ws, name: str) -> SheetInfo:
        info = SheetInfo(name=name)

        # Hidden sheet?
        info.hidden = (ws.sheet_state != "visible")

        dims = ws.dimensions
        if not dims or ws.max_row is None or ws.max_row == 0:
            info.sheet_type = "empty"
            info.notes.append("Sheet appears empty.")
            return info

        info.row_count = ws.max_row
        info.col_count = ws.max_column

        # Merged cells?
        info.has_merged_cells = bool(ws.merged_cells.ranges)

        # Count blank rows in first 50
        blank = 0
        for row in ws.iter_rows(max_row=min(50, ws.max_row), values_only=True):
            if all(v is None or str(v).strip() == "" for v in row):
                blank += 1
        info.blank_row_count = blank

        # Classify sheet
        if ws.max_row < 3 and ws.max_column < 3:
            info.sheet_type = "empty"
        elif self._looks_like_summary(ws):
            info.sheet_type = "summary"
        elif ws.max_row < 5 or ws.max_column < 2:
            info.sheet_type = "lookup"
        else:
            info.sheet_type = "data"

        info.header_row = self._detect_header_row(ws)
        return info

    def _looks_like_summary(self, ws) -> bool:
        """Heuristic: if >30% of cells have formulas (openpyxl data_only masks them), skip."""
        sample_vals = []
        for row in ws.iter_rows(max_row=min(20, ws.max_row), values_only=True):
            sample_vals.extend(v for v in row if v is not None)
        return len(sample_vals) < 5

    def _detect_header_row(self, ws, search_rows: int = 10) -> int:
        """Return 1-based index of the most likely header row."""
        for i, row in enumerate(ws.iter_rows(max_row=search_rows, values_only=True), start=1):
            non_null = [v for v in row if v is not None and str(v).strip() != ""]
            if len(non_null) >= max(2, ws.max_column // 3):
                all_str = all(isinstance(v, str) for v in non_null)
                if all_str:
                    return i
        return 1

    # ── DataFrame loading ─────────────────────────────────────────────────────
    def _load_dataframe(self, ws, info: SheetInfo) -> Optional[pd.DataFrame]:
        try:
            data = list(ws.iter_rows(values_only=True))
            if not data:
                return None

            header_idx = info.header_row - 1   # 0-based
            headers = [
                self._clean_col_name(str(v)) if v is not None else f"Column_{i}"
                for i, v in enumerate(data[header_idx])
            ]

            # Deduplicate headers
            seen: Dict[str, int] = {}
            clean_headers = []
            for h in headers:
                if h in seen:
                    seen[h] += 1
                    clean_headers.append(f"{h}_{seen[h]}")
                    info.duplicate_columns.append(h)
                else:
                    seen[h] = 0
                    clean_headers.append(h)

            rows = data[header_idx + 1:]
            # Drop completely blank rows
            rows = [r for r in rows if any(v is not None and str(v).strip() != "" for v in r)]
            # Pad rows to column count
            ncols = len(clean_headers)
            rows = [list(r) + [None] * (ncols - len(r)) if len(r) < ncols else list(r)[:ncols] for r in rows]

            df = pd.DataFrame(rows, columns=clean_headers)
            return df
        except Exception as exc:
            logger.warning("Could not load sheet '%s' as DataFrame: %s", info.name, exc)
            return None

    # ── Utilities ─────────────────────────────────────────────────────────────
    @staticmethod
    def _clean_col_name(name: str) -> str:
        """Strip extra whitespace and normalize column names."""
        name = name.strip()
        name = re.sub(r"\s+", " ", name)
        return name

    @staticmethod
    def _clean_nulls(df: pd.DataFrame) -> pd.DataFrame:
        """Replace null-string sentinels with NaN."""
        def _replace(val):
            if isinstance(val, str) and val.strip().lower() in NULL_STRINGS:
                return None
            return val
        # applymap was renamed to map in pandas 2.1
        try:
            return df.map(_replace)
        except AttributeError:
            return df.applymap(_replace)

    def _select_primary_sheet(self, result: WorkbookIngestionResult) -> Optional[str]:
        """Choose the largest data sheet by row×column count."""
        best, best_score = None, -1
        for name, df in result.data_frames.items():
            score = df.shape[0] * df.shape[1]
            if score > best_score:
                best_score = score
                best = name
        return best

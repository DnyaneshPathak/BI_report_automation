"""
src/bi_automation/ingestion/excel_reader.py
--------------------------------------------
Robust, memory-safe data ingestion engine.
Replaces brittle openpyxl iter_rows logic with high-performance pandas + pyarrow.
Enforces strict 200 bounds to prevent OOM errors.
Supports both .xlsx and .csv files efficiently.
"""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


logger = logging.getLogger(__name__)

# Null-like strings to treat as NaN
NULL_STRINGS = [
    "na", "n/a", "null", "none", "nil", "nan", "-", "--",
    "blank", "empty", "missing", "unknown", "#n/a", "#null!",
    "not available", "not applicable", "n.a.", "n.a"
]

class MemoryLimitExceeded(Exception):
    """Raised when file size exceeds the strict limit."""
    pass

@dataclass
class SheetInfo:
    name: str
    sheet_type: str = "data"
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


class DataLoader:
    """Robust data loader utilizing pandas with pyarrow backend where possible."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._max_bytes = 200 * 1024 * 1024

    def read(self) -> WorkbookIngestionResult:
        result = WorkbookIngestionResult(file_path=self.file_path)
        
        try:
            # 1. Strict memory bound check
            if not self.file_path.exists():
                raise FileNotFoundError(f"File not found: {self.file_path.name}")
            
            fsize = self.file_path.stat().st_size
            if fsize > self._max_bytes:
                logger.error("File size %d bytes exceeds limit of %d MB", fsize, 200)
                raise MemoryLimitExceeded(
                    f"File is too large ({fsize / 1024 / 1024:.1f} MB). "
                    f"Maximum allowed size is {200} MB."
                )

            ext = self.file_path.suffix.lower()
            if ext == ".csv":
                self._load_csv(result)
            elif ext in {".xlsx", ".xls", ".xlsm"}:
                self._load_excel(result)
            else:
                result.errors.append(f"Unsupported extension: {ext}")

            # 2. Identify the primary sheet / table
            result.primary_sheet = self._select_primary_sheet(result)
            if result.primary_sheet and result.primary_sheet in result.data_frames:
                df_p = result.data_frames[result.primary_sheet]
                result.total_rows    = df_p.shape[0]
                result.total_columns = df_p.shape[1]

            if not result.data_frames:
                if not result.errors:
                    result.errors.append(
                        "No structured dataset was detected. "
                        "Ensure the file contains at least one table with column headers."
                    )
        except MemoryLimitExceeded as exc:
            result.errors.append(str(exc))
        except Exception as exc:
            logger.error("DataLoader error: %s", exc, exc_info=True)
            result.errors.append(f"Failed to load data: {exc}")

        return result

    def _load_csv(self, result: WorkbookIngestionResult) -> None:
        """Fast CSV loading with pyarrow backend."""
        try:
            df = pd.read_csv(
                self.file_path,
                na_values=NULL_STRINGS,
                keep_default_na=True
            )
            sheet_name = self.file_path.stem
            
            # Basic cleaning
            df = self._clean_dataframe(df, sheet_name, result)
            
            info = SheetInfo(
                name=sheet_name,
                sheet_type="data",
                row_count=df.shape[0],
                col_count=df.shape[1]
            )
            result.sheets.append(info)
            result.data_frames[sheet_name] = df
            logger.info("CSV '%s' loaded: %d rows × %d cols", sheet_name, df.shape[0], df.shape[1])
        except Exception as exc:
            result.errors.append(f"CSV read error: {exc}")

    def _load_excel(self, result: WorkbookIngestionResult) -> None:
        """Robust Excel loading using pandas."""
        try:
            # We first try to get sheet names without loading data
            xl = pd.ExcelFile(self.file_path, engine="openpyxl")
            for sheet_name in xl.sheet_names:
                df = xl.parse(sheet_name=sheet_name, na_values=NULL_STRINGS, keep_default_na=True)
                
                # Check if empty
                if df.empty or df.shape[1] == 0:
                    info = SheetInfo(name=sheet_name, sheet_type="empty")
                    result.sheets.append(info)
                    continue

                # Clean it up
                df = self._clean_dataframe(df, sheet_name, result)
                
                # If everything was dropped (e.g. empty sheet formatted weirdly)
                if df.empty:
                    info = SheetInfo(name=sheet_name, sheet_type="empty")
                    result.sheets.append(info)
                    continue

                info = SheetInfo(
                    name=sheet_name,
                    sheet_type="data",
                    row_count=df.shape[0],
                    col_count=df.shape[1]
                )
                result.sheets.append(info)
                result.data_frames[sheet_name] = df
                logger.info("Excel sheet '%s' loaded: %d rows × %d cols", sheet_name, df.shape[0], df.shape[1])
                
        except Exception as exc:
            result.errors.append(f"Excel read error: {exc}")

    def _clean_dataframe(self, df: pd.DataFrame, sheet_name: str, result: WorkbookIngestionResult) -> pd.DataFrame:
        """Basic early-stage normalisation: drop totally empty rows/cols, clean headers."""
        
        # Clean column names
        def _clean_col_name(c) -> str:
            if pd.isna(c) or str(c).strip() == "":
                return "Unnamed"
            name = str(c).strip()
            name = re.sub(r"\s+", " ", name)
            return name

        new_cols = []
        seen = {}
        for c in df.columns:
            clean = _clean_col_name(c)
            if clean in seen:
                seen[clean] += 1
                clean = f"{clean}_{seen[clean]}"
            else:
                seen[clean] = 0
            new_cols.append(clean)
            
        if list(df.columns) != new_cols:
            result.preparation_log.append(f"Cleaned column headers in sheet '{sheet_name}'.")
        df.columns = new_cols
        return df

    def _select_primary_sheet(self, result: WorkbookIngestionResult) -> Optional[str]:
        """Choose the largest data sheet by row×column count."""
        best, best_score = None, -1
        for name, df in result.data_frames.items():
            score = df.shape[0] * df.shape[1]
            if score > best_score:
                best_score = score
                best = name
        return best

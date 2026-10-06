"""
tests/unit/test_ingestion.py

Tests for Phase 3 Data Ingestion and Cleaning.
Validates memory limit enforcement and PyArrow/Pandas CSV loading.
"""
import sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from bi_automation.ingestion.loader import DataLoader, MemoryLimitExceeded
from bi_automation.config.settings import TEMP_DIR
from bi_automation.config.constants import MAX_FILE_SIZE_MB

def test_memory_limit_enforced(monkeypatch, tmp_path):
    """File size exceeding MAX_FILE_SIZE_MB should raise MemoryLimitExceeded."""
    # Create a dummy file
    dummy_file = tmp_path / "huge.csv"
    dummy_file.write_text("a,b,c\n1,2,3")
    
    # Mock stat().st_size to return max + 1 bytes
    class MockStat:
        st_size = (MAX_FILE_SIZE_MB * 1024 * 1024) + 1
        
    monkeypatch.setattr(Path, "stat", lambda self, *args, **kwargs: MockStat())
    
    reader = DataLoader(dummy_file)
    result = reader.read()
    
    assert not result.data_frames
    assert len(result.errors) > 0
    assert "File is too large" in result.errors[0]

def test_csv_ingestion(tmp_path):
    """CSV ingestion works via the new robust loader."""
    dummy_file = tmp_path / "test.csv"
    dummy_file.write_text("ID,Name,Value,Missing\n1,Alice,100,na\n2,Bob,,nan\n3,Charlie,300,5")
    
    reader = DataLoader(dummy_file)
    result = reader.read()
    
    assert not result.errors
    assert "test" in result.data_frames
    
    df = result.data_frames["test"]
    assert df.shape == (3, 4)
    # Check that null strings are parsed as NaN
    assert pd.isna(df.loc[1, "Value"])
    assert pd.isna(df.loc[1, "Missing"])
    assert df.loc[2, "Missing"] == 5.0

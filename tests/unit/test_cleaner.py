"""
tests/unit/test_cleaner.py

Tests for Phase 3 Data Cleaner and Missing Value imputation.
Ensures missing values are explicitly tracked, and types are cast safely.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from bi_automation.preprocessing.cleaner import DataCleaner
from bi_automation.preprocessing.missing_values import MissingValueHandler
from bi_automation.preprocessing.type_detector import ColumnProfile

def test_cleaner_datetime_parsing():
    """Ensure cleaner uses safe format='mixed' without crashing on bad dates."""
    df = pd.DataFrame({
        "DateCol": ["2023-01-01", "2023/12/31", "InvalidDate", "2024-02-29"]
    })
    
    profiles = {
        "DateCol": ColumnProfile(name="DateCol", analytical_type="datetime")
    }
    
    cleaner = DataCleaner(df, profiles)
    cleaned_df, log = cleaner.clean()
    
    # "InvalidDate" should be coerced to NaT safely
    assert pd.isna(cleaned_df.loc[2, "DateCol"])
    # Valid dates should be parsed
    assert cleaned_df.loc[0, "DateCol"].year == 2023
    assert cleaned_df.loc[3, "DateCol"].month == 2
    
    # Check that a log was made
    assert any("converted to datetime" in line for line in log)

def test_missing_values_explicit_logging():
    """Ensure missing value imputation doesn't happen silently."""
    df = pd.DataFrame({
        "Numeric": [1.0, 2.0, np.nan, 4.0, 5.0],
        "Category": ["A", "B", np.nan, "A", "A"]
    })
    
    profiles = {
        "Numeric": ColumnProfile(name="Numeric", analytical_type="continuous", include_in_analysis=True),
        "Category": ColumnProfile(name="Category", analytical_type="categorical_nominal", include_in_analysis=True)
    }
    
    handler = MissingValueHandler(df, profiles)
    imputed_df, log, summary = handler.analyse_and_impute()
    
    # Median of [1,2,4,5] is 3.0
    assert imputed_df.loc[2, "Numeric"] == 3.0
    # Mode is A
    assert imputed_df.loc[2, "Category"] == "A"
    
    # Verify exact log messages
    assert any("imputed 1 missing value(s) with median (3.00)" in line for line in log)
    assert any("imputed 1 missing value(s) with mode ('A')" in line for line in log)

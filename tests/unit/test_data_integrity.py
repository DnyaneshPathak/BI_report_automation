import sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / 'src'))

from bi_automation.services.pipeline import AnalysisPipeline

def test_pipeline_non_mutating_loader(tmp_path):
    # Create a synthetic dataset with missing values and potential outliers
    df = pd.DataFrame({
        'A': [1.0, 2.0, None, 4.0, 100.0],
        'B': ['x', 'y', 'z', None, 'x']
    })
    
    file_path = tmp_path / 'synthetic.csv'
    df.to_csv(file_path, index=False)
    
    pipeline = AnalysisPipeline(file_path)
    result = pipeline.run_phase1()
    
    assert result.success is True, result.error
    assert result.rows_loaded == 5
    assert result.rows_used == 5
    assert result.rows_filtered_by_request == 0
    
    # Check if invariants hold
    assert result.rows_used + result.rows_filtered_by_request == result.rows_loaded
    
    # Check that data hasn't been mutated (no rows dropped, no imputation)
    df_clean = result.df_clean
    assert len(df_clean) == 5
    assert pd.isna(df_clean.loc[2, 'A'])  # Not imputed
    assert df_clean.loc[4, 'A'] == 100.0   # Not removed as outlier
    
    assert len(result.preparation_log) > 0


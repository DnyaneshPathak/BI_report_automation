import pytest
import pandas as pd
from bi_automation.engine.executor import PlanExecutor

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Region": ["North", "South", "East", "West", "North"],
        "Sales": [100, 200, 150, 50, 300],
        "Category": ["A", "B", "A", "A", "C"],
        "Order Date": pd.to_datetime(["2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01", "2023-05-01"])
    })

def test_execute_kpi(sample_df):
    plan = {
        "items": [
            {
                "id": "k1",
                "type": "kpi",
                "metric": {"column": "Sales", "agg": "sum"},
                "title": "Total Sales"
            }
        ]
    }
    
    executor = PlanExecutor(sample_df)
    results = executor.execute(plan)
    
    assert "k1" in results
    assert results["k1"]["value"] == 800.0

def test_execute_visual(sample_df):
    plan = {
        "items": [
            {
                "id": "v1",
                "type": "visual",
                "chart": "bar",
                "x": {"column": "Region"},
                "y": [{"column": "Sales", "agg": "sum"}],
                "sort": {"by": "Sales", "dir": "desc"},
                "top_n": 2
            }
        ]
    }
    
    executor = PlanExecutor(sample_df)
    results = executor.execute(plan)
    
    assert "v1" in results
    v1_res = results["v1"]["dataset"]
    # North should be 400, South 200
    source = v1_res["source"]
    assert source[0] == ["Region", "sum_Sales"]
    assert source[1] == ["North", 400]
    assert source[2] == ["South", 200]
    assert len(source) == 3 # header + top 2

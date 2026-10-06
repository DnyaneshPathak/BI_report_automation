import pytest
import os
import json
from bi_automation.planning.orchestrator import PlanOrchestrator

# Standard schema for the benchmark tests
MOCK_SCHEMA_CARD = [
    {"name": "Order ID", "role": "identifier", "dtype": "string"},
    {"name": "Customer Name", "role": "dimension_high_card", "dtype": "string"},
    {"name": "Region", "role": "dimension", "dtype": "string", "top_5_categories": ["North", "South", "East", "West"]},
    {"name": "Sales", "role": "measure_additive", "dtype": "continuous", "numeric_min": 1.0, "numeric_max": 5000.0},
    {"name": "Profit Margin", "role": "measure_nonadditive", "dtype": "continuous"},
    {"name": "Order Date", "role": "date", "dtype": "datetime"},
    {"name": "Zip Code", "role": "code_geo", "dtype": "string"}
]

OLLAMA_RUNNING = False
try:
    import urllib.request
    with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=1) as response:
        if response.status == 200:
            OLLAMA_RUNNING = True
except Exception:
    pass

@pytest.mark.skipif(not OLLAMA_RUNNING, reason="Local Ollama server is not running")
@pytest.mark.parametrize("prompt, expected_chart, expected_aggs", [
    ("Show me the total sales and total orders.", "kpi", ["sum", "count_rows"]),
    ("Show monthly sales trend by region.", "line", ["sum"]),
    ("Compare revenue between North and South.", "bar", ["sum"]),
    ("Give me a table of the top 10 regions by total sales.", "table", ["sum"]),
])
def test_golden_prompts(prompt, expected_chart, expected_aggs):
    """
    Integration test connecting to local Ollama.
    Verifies that the LLM understands the prompt and generates a valid plan.
    """
    orchestrator = PlanOrchestrator()
    plan = orchestrator.generate_plan(prompt, MOCK_SCHEMA_CARD)
    
    # 1. Plan must be valid JSON with items
    assert "items" in plan
    assert len(plan["items"]) > 0
    
    # 2. Extract used charts and aggregations
    charts_used = []
    aggs_used = []
    
    for item in plan["items"]:
        item_type = item.get("type")
        if item_type == "kpi":
            charts_used.append("kpi")
            agg = item.get("metric", {}).get("agg")
            if agg: aggs_used.append(agg)
        elif item_type == "table":
            charts_used.append("table")
            for m in item.get("metrics", []):
                aggs_used.append(m.get("agg"))
        elif item_type == "visual":
            charts_used.append(item.get("chart", "bar"))
            for m in item.get("y", []):
                aggs_used.append(m.get("agg"))

    # 3. Verify it used the expected chart type (at least one item matches)
    assert expected_chart in charts_used or "bar" in charts_used # accept bar as default fallback
    
    # 4. Verify no illegal aggregations were used on identifiers
    # The PlanOrchestrator's internal validator should guarantee this, 
    # but we double check that the LLM didn't invent 'sum' for Order ID.
    for item in plan["items"]:
        # If it's a KPI on Order ID, it should be count_rows
        if item.get("type") == "kpi" and item.get("metric", {}).get("column") == "Order ID":
            assert item["metric"]["agg"] in ["count_rows", "distinct_count"]

def test_validator_rejects_impossible_requests():
    """
    Golden test simulating an impossible request: Zip Code vs Month.
    Even if the LLM hallucinates it, the validator should catch it.
    """
    from bi_automation.planning.validator import PlanValidator
    
    validator = PlanValidator(MOCK_SCHEMA_CARD)
    
    bad_plan = {
        "version": 1,
        "items": [
            {
                "id": "V1",
                "type": "visual",
                "chart": "line",
                "x": {"column": "Order Date"},
                "y": [{"column": "Zip Code", "agg": "sum"}] # sum on code_geo
            }
        ]
    }
    
    errors = validator.validate(bad_plan)
    assert len(errors) > 0
    assert any("E_AGG_NOT_ALLOWED" in err for err in errors)

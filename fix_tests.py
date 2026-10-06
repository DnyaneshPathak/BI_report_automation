import os

file_path = 'tests/unit/test_orchestrator.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_tests = '''
def test_prune_invalid_items_mixed():
    from bi_automation.planning.validator import PlanValidator
    schema = [{"name": "Sales", "role": "measure_additive"}, {"name": "Ticket No", "role": "identifier"}]
    validator = PlanValidator(schema)
    
    plan = {
        "version": 1,
        "needs_clarification": None,
        "items": [
            {
                "id": "K1",
                "type": "kpi",
                "metric": {"column": "Ticket No", "agg": "count_rows"} # Valid
            },
            {
                "id": "K2",
                "type": "kpi",
                "metric": {"column": "Ticket No", "agg": "sum"} # Invalid
            },
            {
                "id": "V1",
                "type": "visual",
                "chart": "bar",
                "x": {"column": "Ticket No"},
                "y": [{"column": "Sales", "agg": "sum"}] # Valid
            }
        ]
    }
    
    orchestrator = PlanOrchestrator(planner=None, critic=None)
    pruned_plan = orchestrator._prune_invalid_items(plan, validator)
    
    assert len(pruned_plan["items"]) == 2
    assert pruned_plan["items"][0]["id"] == "K1"
    assert pruned_plan["items"][1]["id"] == "V1"

def test_prune_invalid_items_empty():
    from bi_automation.planning.validator import PlanValidator
    validator = PlanValidator([])
    
    plan = {"version": 1} # No items key
    
    orchestrator = PlanOrchestrator(planner=None, critic=None)
    pruned_plan = orchestrator._prune_invalid_items(plan, validator)
    
    assert "items" in pruned_plan
    assert len(pruned_plan["items"]) == 0
'''

if 'test_prune_invalid_items_mixed' not in content:
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n" + new_tests)

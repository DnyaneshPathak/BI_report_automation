import pytest
from bi_automation.planning.orchestrator import PlanOrchestrator
from bi_automation.llm.planner import DashboardPlanner
from bi_automation.llm.critic import PlanCritic

class MockOllamaClient:
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0
        
    def generate(self, prompt, schema=None, temperature=0.0):
        resp = self.responses[self.call_count]
        self.call_count += 1
        return resp

def test_orchestrator_valid_first_try():
    schema = [{"name": "Sales", "role": "measure_additive"}, {"name": "Region", "role": "dimension"}]
    mock_responses = [{
        "version": 1,
        "needs_clarification": None,
        "requirements": [],
        "filters": [],
        "assumptions": [],
        "items": [
            {"id": "V1", "requirement": "R1", "type": "visual", "title": "Sales by Region", "confidence": 1.0, 
             "x": {"column": "Region"}, "y": [{"column": "Sales", "agg": "sum"}]}
        ]
    }]
    client = MockOllamaClient(mock_responses)
    orchestrator = PlanOrchestrator(planner=DashboardPlanner(client), critic=PlanCritic(client))
    
    plan = orchestrator.generate_plan("Show sales by region", schema)
    
    assert len(plan["items"]) == 1
    assert client.call_count == 1

def test_orchestrator_repair_loop():
    schema = [{"name": "Ticket No", "role": "identifier"}]
    mock_responses = [
        # 1. First attempt: Invalid (sum on identifier)
        {
            "version": 1,
            "needs_clarification": None,
            "requirements": [],
            "filters": [],
            "assumptions": [],
            "items": [
                {"id": "K1", "requirement": "R1", "type": "kpi", "title": "Total Tickets", "confidence": 1.0, 
                 "metric": {"column": "Ticket No", "agg": "sum"}}
            ]
        },
        # 2. Second attempt: Valid (count_rows)
        {
            "version": 1,
            "needs_clarification": None,
            "requirements": [],
            "filters": [],
            "assumptions": [],
            "items": [
                {"id": "K1", "requirement": "R1", "type": "kpi", "title": "Total Tickets", "confidence": 1.0, 
                 "metric": {"column": "Ticket No", "agg": "count_rows"}}
            ]
        }
    ]
    client = MockOllamaClient(mock_responses)
    orchestrator = PlanOrchestrator(planner=DashboardPlanner(client), critic=PlanCritic(client))
    
    plan = orchestrator.generate_plan("Total tickets", schema)
    
    assert len(plan["items"]) == 1
    assert plan["items"][0]["metric"]["agg"] == "count_rows"
    assert client.call_count == 2

def test_orchestrator_prunes_invalid_item_after_max_repairs():
    schema = [{"name": "Ticket No", "role": "identifier"}]
    # Always invalid response
    mock_responses = [
        {
            "version": 1,
            "needs_clarification": None,
            "requirements": [],
            "filters": [],
            "assumptions": [],
            "items": [
                {"id": "K1", "requirement": "R1", "type": "kpi", "title": "Total Tickets", "confidence": 1.0, 
                 "metric": {"column": "Ticket No", "agg": "sum"}}
            ]
        }
    ] * 3
    client = MockOllamaClient(mock_responses)
    orchestrator = PlanOrchestrator(planner=DashboardPlanner(client), critic=PlanCritic(client))
    
    plan = orchestrator.generate_plan("Total tickets", schema, max_repairs=2)
    
    assert len(plan["items"]) == 0
    assert client.call_count == 3


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

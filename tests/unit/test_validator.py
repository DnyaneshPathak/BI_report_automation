import pytest
from bi_automation.planning.validator import PlanValidator, ValidationError

def test_validator_valid_plan():
    schema = [
        {"name": "Sales", "role": "measure_additive"},
        {"name": "Region", "role": "dimension"},
        {"name": "Ticket No", "role": "identifier"}
    ]
    
    plan = {
        "version": 1,
        "needs_clarification": None,
        "items": [
            {
                "id": "V1",
                "x": {"column": "Region"},
                "y": [{"column": "Sales", "agg": "sum"}]
            },
            {
                "id": "K1",
                "metric": {"column": "Ticket No", "agg": "count_rows"}
            }
        ]
    }
    
    validator = PlanValidator(schema)
    errors = validator.validate(plan)
    assert len(errors) == 0

def test_validator_invalid_column():
    schema = [{"name": "Sales", "role": "measure_additive"}]
    plan = {
        "items": [
            {"x": {"column": "Region"}} # Region does not exist
        ]
    }
    validator = PlanValidator(schema)
    errors = validator.validate(plan)
    assert len(errors) == 1
    assert "does not exist in schema" in errors[0]

def test_validator_invalid_agg():
    schema = [{"name": "Ticket No", "role": "identifier"}]
    plan = {
        "items": [
            {"metric": {"column": "Ticket No", "agg": "sum"}} # Sum not allowed for identifier
        ]
    }
    validator = PlanValidator(schema)
    errors = validator.validate(plan)
    assert len(errors) == 1
    assert "E_AGG_NOT_ALLOWED" in errors[0]
    assert "identifier" in errors[0]

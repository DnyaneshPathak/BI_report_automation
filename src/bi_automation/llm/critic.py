import json
import logging
from typing import Dict, Any, List

from bi_automation.llm.client import OllamaClient
from bi_automation.planning.schema import PLANNER_JSON_SCHEMA

logger = logging.getLogger(__name__)

class PlanCritic:
    """Uses Ollama to repair a plan that failed deterministic validation."""
    
    def __init__(self, ollama_client: OllamaClient = None):
        self.client = ollama_client or OllamaClient()

    def _build_system_prompt(self) -> str:
        return """You are a strict data validation agent. 
You are given a JSON plan for a BI dashboard, the dataset schema, and a list of ERROR CODES from a deterministic validator.
Your job is to FIX the plan so that it passes validation.

RULES:
1. If a column does not exist, find the correct column name in the schema (e.g. spelling error), or drop the item if it's impossible.
2. If there is an E_AGG_NOT_ALLOWED error, change the aggregation to one of the ALLOWED aggregations listed in the error message.
3. Return the corrected plan in the EXACT SAME JSON schema.
4. Do not invent new requirements.
"""

    def repair(self, original_plan: Dict[str, Any], schema_card: List[Dict[str, Any]], errors: List[str]) -> Dict[str, Any]:
        """Generate a repaired dashboard plan."""
        
        system_prompt = self._build_system_prompt()
        
        schema_json = json.dumps(schema_card, indent=2)
        plan_json = json.dumps(original_plan, indent=2)
        errors_text = "\n".join(errors)
        
        full_prompt = (
            f"{system_prompt}\n\n"
            f"DATASET SCHEMA:\n{schema_json}\n\n"
            f"ORIGINAL PLAN:\n{plan_json}\n\n"
            f"VALIDATION ERRORS:\n{errors_text}\n\n"
            "Please provide the corrected JSON plan."
        )
        
        try:
            response = self.client.generate(
                prompt=full_prompt, 
                schema=PLANNER_JSON_SCHEMA, 
                temperature=0.0
            )
            return response
            
        except Exception as e:
            logger.error(f"Critic failed: {e}")
            raise

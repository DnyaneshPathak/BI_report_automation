import logging
from typing import Dict, Any, List

from bi_automation.llm.planner import DashboardPlanner
from bi_automation.llm.critic import PlanCritic
from bi_automation.planning.validator import PlanValidator

logger = logging.getLogger(__name__)

class PlanOrchestrator:
    """Orchestrates the LLM Planner, deterministic validation, and LLM Critic repair loop."""
    
    def __init__(self, planner: DashboardPlanner = None, critic: PlanCritic = None):
        self.planner = planner or DashboardPlanner()
        self.critic = critic or PlanCritic()
        
    def generate_plan(self, user_prompt: str, schema_card: List[Dict[str, Any]], max_repairs: int = 2) -> Dict[str, Any]:
        """Generate a valid plan, repairing up to max_repairs times if invalid."""
        
        logger.info("Generating initial plan via LLM...")
        plan = self.planner.plan(user_prompt, schema_card)
        
        validator = PlanValidator(schema_card)
        errors = validator.validate(plan)
        
        if not errors:
            logger.info("Initial plan passed validation.")
            return plan
            
        repair_count = 0
        while errors and repair_count < max_repairs:
            repair_count += 1
            logger.warning(f"Plan validation failed with {len(errors)} errors. Initiating repair loop {repair_count}/{max_repairs}.")
            
            try:
                plan = self.critic.repair(plan, schema_card, errors)
                errors = validator.validate(plan)
            except Exception as e:
                logger.error(f"Critic repair failed: {e}")
                break
                
        if errors:
            logger.warning(f"Plan still has {len(errors)} errors after {repair_count} repairs. Pruning invalid items.")
            plan = self._prune_invalid_items(plan, validator)
            
        return plan
        
    def _prune_invalid_items(self, plan: Dict[str, Any], validator: PlanValidator) -> Dict[str, Any]:
        """Remove specific items that fail validation."""
        valid_items = []
        for item in plan.get("items", []):
            item_errors = validator.validate({"version": 1, "needs_clarification": None, "requirements": [], "filters": [], "assumptions": [], "items": [item]})
            if not item_errors:
                valid_items.append(item)
            else:
                logger.warning(f"Pruned invalid item {item.get('id')}: {item_errors}")
        
        plan["items"] = valid_items
        return plan

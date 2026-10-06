import json
import logging
from typing import Dict, Any, List

from bi_automation.llm.client import OllamaClient
from bi_automation.planning.schema import PLANNER_JSON_SCHEMA

logger = logging.getLogger(__name__)

class DashboardPlanner:
    """Uses Ollama to turn a user prompt into a structured dashboard plan."""
    
    def __init__(self, ollama_client: OllamaClient = None):
        self.client = ollama_client or OllamaClient()

    def _build_system_prompt(self) -> str:
        return """You are an expert Business Intelligence dashboard planner.
Your goal is to translate a user's natural language request into a deterministic JSON plan.

RULES:
1. ONLY produce what the user explicitly requested. Do not invent extra charts or insights.
2. Every item must trace back to a requirement ID. Create one item per requested chart.
3. You must use ONLY the columns provided in the dataset schema. Do not invent columns.
4. If a request is completely ambiguous or impossible given the schema, fill the "needs_clarification" field and leave requirements/items empty.

AGGREGATION RULES by column role:
   - Identifier: count_rows, distinct_count, count_non_null, none
   - Measure / Financial Measure / Quantity / Target-Like Metric: sum, avg, median, min, max, count_non_null, none
   - Dimension / Location / Status / Binary: count_rows, distinct_count, pct_of_total, none
   - Date / Datetime: min, max, count_rows, distinct_count, none

CHART TYPE GUIDANCE:
   - "scatter plot" → type: "visual", chart: "scatter". Set x to the first numeric column, y[0] with the second numeric column and agg: "none". DO NOT aggregate scatter data.
   - "count plot" / "bar count" / "distribution" of a categorical → type: "visual", chart: "bar". Set x to the categorical column, y[0] with the SAME categorical column and agg: "count_rows".
   - "bar chart" → type: "visual", chart: "bar"
   - "line chart" → type: "visual", chart: "line"
   - "pie chart" → type: "visual", chart: "pie"
   - "table" → type: "table"

When a user asks for MULTIPLE charts in one request, produce one item per chart in the "items" array.

Output valid JSON exactly matching the requested schema.
"""

    def plan(self, user_prompt: str, schema_card: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a dashboard plan from the user prompt and dataset schema."""
        
        system_prompt = self._build_system_prompt()
        
        # Build the final prompt by injecting the schema and the user's request
        schema_json = json.dumps(schema_card, indent=2)
        full_prompt = f"{system_prompt}\n\nDATASET SCHEMA:\n{schema_json}\n\nUSER REQUEST:\n{user_prompt}\n"
        
        try:
            # We enforce structured generation
            response = self.client.generate(
                prompt=full_prompt, 
                schema=PLANNER_JSON_SCHEMA, 
                temperature=0.0
            )
            return response
            
        except Exception as e:
            logger.error(f"Planner failed: {e}")
            raise

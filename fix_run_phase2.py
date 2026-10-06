import os
import re

file_path = 'src/bi_automation/services/pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''    def run_phase2(self, prompt: str) -> 'PipelineResult':
        assert self.result.rows_used + self.result.rows_filtered_by_request == self.result.rows_loaded, "Invariant violated: hidden row drop detected."
        
        from bi_automation.planning.orchestrator import PlanOrchestrator
        orchestrator = PlanOrchestrator()
        
        self.progress_callback("Planning", "running", "Analyzing your request...")
        try:
            plan = orchestrator.generate_plan(prompt, self.result.schema_card)
            self.result.plan = plan
            self.progress_callback("Planning", "done", "Plan generated")
        except Exception as e:
            self.progress_callback("Planning", "error", str(e))
            self.result.error = str(e)
            self.result.success = False
            return self.result

        # Skip execution for now as it requires the Executor module (Phase 5/7)
        self.result.success = True
        return self.result
'''

# Find run_phase2 and replace until _execute_steps
content = re.sub(r'    def run_phase2\(self, prompt: str\) -> PipelineResult:.*?        return self.result', replacement, content, flags=re.DOTALL, count=1)

# Add plan to PipelineResult
if 'plan: Dict[str, Any]' not in content:
    content = content.replace('schema_card: List[Dict[str, Any]] = field(default_factory=list)', 'schema_card: List[Dict[str, Any]] = field(default_factory=list)\n    plan: Dict[str, Any] = field(default_factory=dict)')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated run_phase2 in pipeline.py")

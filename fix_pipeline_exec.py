import os
import re

file_path = 'src/bi_automation/services/pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''
        try:
            from bi_automation.engine.executor import PlanExecutor
            self.progress_callback("Executing", "running", "Computing figures securely...")
            executor = PlanExecutor(self.result.df_clean)
            computed_figures = executor.execute(plan)
            self.result.computed_figures = computed_figures
            self.progress_callback("Executing", "done", "Execution complete")
        except Exception as e:
            self.progress_callback("Executing", "error", str(e))
            self.result.error = str(e)
            self.result.success = False
            return self.result

        self.result.success = True
        return self.result
'''

content = re.sub(r'        # Skip execution for now as it requires the Executor module \(Phase 5/7\).*?        return self.result', replacement, content, flags=re.DOTALL)

# Add computed_figures to PipelineResult
if 'computed_figures: Dict[str, Any]' not in content:
    content = content.replace('plan: Dict[str, Any] = field(default_factory=dict)', 'plan: Dict[str, Any] = field(default_factory=dict)\n    computed_figures: Dict[str, Any] = field(default_factory=dict)')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated pipeline.py to call Executor")

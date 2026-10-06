import os
import re

file_path = 'src/bi_automation/services/pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

execute_steps_replacement = '''    def _execute_steps(self, steps):
        for step_name, step_fn in steps:
            step = StepStatus(name=step_name, status="running")
            self.result.steps.append(step)
            self.progress_callback(step_name, "running", "")
            t0 = time.time()
            try:
                step_fn()
                step.status     = "done"
                step.duration_s = round(time.time() - t0, 2)
                self.progress_callback(step_name, "done", f"{step.duration_s}s")
                logger.info("[PASS] %s (%.1fs)", step_name, step.duration_s)
            except Exception as exc:
                step.status  = "error"
                step.message = str(exc)
                logger.error("? %s: %s", step_name, exc, exc_info=True)
                self.progress_callback(step_name, "error", str(exc))
                if step_name in ("Reading Data", "Reading Excel"):
                    self.result.error = f"Pipeline aborted: {exc}"
                    return
'''

content = re.sub(r'    def _execute_steps\(self, steps\):.*?    # -- Steps --', execute_steps_replacement + '\n    # -- Steps --', content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed _execute_steps")

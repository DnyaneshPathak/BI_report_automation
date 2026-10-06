import os
import re

file_path = 'src/bi_automation/powerbi/model_builder.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''    def _build_report_layout(self) -> dict:
        sections = []
        visuals = self._build_page_visuals()
        sections.append({
            "name": str(uuid.uuid4()),
            "displayName": self.dashboard_title,
            "ordinal": 0,
            "visualContainers": visuals,
            "config": json.dumps({
                "defaultDrillFilterOtherVisuals": True,
                "background": {"transparency": 100},
            }),
        })

        return {
            "id": str(uuid.uuid4()),
            "reportId": str(uuid.uuid4()),
            "config": json.dumps({
                "version": "5.43",
                "themeCollection": {"baseTheme": {"name": "CY22SU03", "version": "5.43"}},
            }),
            "sections": sections,
        }
'''

content = re.sub(r'    def _build_report_layout\(self\) -> dict:.*?        return {', replacement + '        return {', content, flags=re.DOTALL)
# wait the regex matched 'return {' so it was replaced. I added it back in the replacement string but I should be careful.
# Let's fix the replacement string.

replacement_fixed = '''    def _build_report_layout(self) -> dict:
        sections = []
        visuals = self._build_page_visuals()
        sections.append({
            "name": str(uuid.uuid4()),
            "displayName": self.dashboard_title,
            "ordinal": 0,
            "visualContainers": visuals,
            "config": json.dumps({
                "defaultDrillFilterOtherVisuals": True,
                "background": {"transparency": 100},
            }),
        })

        return {
            "id": str(uuid.uuid4()),
            "reportId": str(uuid.uuid4()),
            "config": json.dumps({
                "version": "5.43",
                "themeCollection": {"baseTheme": {"name": "CY22SU03", "version": "5.43"}},
            }),
            "sections": sections,
        }
'''

content = re.sub(r'    def _build_report_layout\(self\) -> dict:.*?            "sections": sections,\n        }', replacement_fixed, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated _build_report_layout")

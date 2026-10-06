import os
import re

file_path = 'src/bi_automation/engine/executor.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''
        # Verify step
        warnings = []
        if grouped.empty:
            warnings.append("Result is empty.")
        elif grouped.isnull().all().all():
            warnings.append("Result contains only null values.")
            
        dataset = {
            "source": [grouped.columns.tolist()] + grouped.replace({np.nan: None}).values.tolist()
        }
        
        # Calculate Layout
        try:
            from bi_automation.charts.layout import compute_grid_margins
            x_labels = grouped[group_cols[0]].tolist() if group_cols else []
            layout_meta = compute_grid_margins(x_labels)
        except Exception:
            layout_meta = {}
        
        return {
            "dataset": dataset,
            "title": item.get("title", ""),
            "chart_type": item.get("chart", "bar") if item.get("type") == "visual" else "table",
            "warnings": warnings,
            "layout": layout_meta
        }
'''

content = re.sub(r'        # Verify step.*?        }', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated executor.py to include layout_meta")

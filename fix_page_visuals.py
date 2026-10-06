import os
import re

file_path = 'src/bi_automation/powerbi/model_builder.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''    def _build_page_visuals(self) -> List[dict]:
        visuals = []
        pad = 16
        y_offset = 10
        
        from bi_automation.charts.registry import get_chart_def
        
        items = self.plan.get("items", [])
        
        # Add KPI cards
        kpis = [item for item in items if item.get("type") == "kpi"]
        if kpis:
            kpi_w = 220
            kpi_h = 80
            for i, kpi in enumerate(kpis[:4]):
                x = pad + i * (kpi_w + pad)
                y = y_offset
                visual_name = kpi.get("id", f"kpi_{i}")
                
                metric = kpi.get("metric", {})
                measure_name = f"{metric.get('agg', 'sum')}_{metric.get('column', '')}"
                
                visuals.append({
                    "x": x, "y": y,
                    "z": 100 + i,
                    "width": kpi_w,
                    "height": kpi_h,
                    "config": json.dumps({
                        "name": visual_name,
                        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": kpi_w, "height": kpi_h}}],
                        "singleVisual": {
                            "visualType": "card",
                            "projections": {
                                "Values": [{"queryRef": measure_name}],
                            },
                            "prototypeQuery": {
                                "Version": 2,
                                "From": [{"Name": "t", "Entity": self.table_name, "Type": 0}],
                                "Select": [
                                    {"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": measure_name}, "Name": measure_name}
                                ],
                            },
                            "title": {"show": False},
                        },
                    }),
                })
            y_offset += kpi_h + pad

        cols = 2
        cell_w, cell_h = 440, 260
        
        charts = [item for item in items if item.get("type") in ("visual", "table")]
        
        for i, item in enumerate(charts[:6]):
            row = i // cols
            col = i % cols
            x = pad + col * (cell_w + pad)
            y = y_offset + row * (cell_h + pad)
            
            chart_type = item.get("chart", "bar") if item.get("type") == "visual" else "table"
            chart_def = get_chart_def(chart_type)
            visual_type = chart_def.pbi_visual_type if chart_def else "clusteredBarChart"
            
            visual_name = item.get("id", f"vis_{i}")
            
            # Very basic projection building
            x_col = item.get("x", {}).get("column") if isinstance(item.get("x"), dict) else item.get("x")
            y_items = item.get("y", [])
            y_col = y_items[0].get("column") if y_items and isinstance(y_items, list) else (y_items.get("column") if isinstance(y_items, dict) else None)
            
            measure_name = f"sum_{y_col}" if y_col else "CountRows" # placeholder
            
            projections = {
                "Category": [{"queryRef": x_col}],
                "Y": [{"queryRef": measure_name}],
            } if x_col and y_col else {}
            
            if visual_type in ("donutChart", "pieChart", "treemap"):
                projections = {
                    "Category": [{"queryRef": x_col}],
                    "Y": [{"queryRef": measure_name}],
                }
            elif visual_type == "scatterChart":
                projections = {
                    "Category": [{"queryRef": x_col}],
                    "X": [{"queryRef": x_col}],
                    "Y": [{"queryRef": measure_name}],
                }
                
            select_arr = []
            if x_col: select_arr.append({"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": x_col}, "Name": x_col})
            if measure_name: select_arr.append({"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": measure_name}, "Name": measure_name})
            
            visuals.append({
                "x": x, "y": y,
                "z": 1000 + i,
                "width": cell_w,
                "height": cell_h,
                "config": json.dumps({
                    "name": visual_name,
                    "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": cell_w, "height": cell_h}}],
                    "singleVisual": {
                        "visualType": visual_type,
                        "projections": projections,
                        "prototypeQuery": {
                            "Version": 2,
                            "From": [{"Name": "t", "Entity": self.table_name, "Type": 0}],
                            "Select": select_arr,
                        },
                        "title": {"show": True, "text": item.get("title", "")},
                    },
                }),
            })
        return visuals
'''

content = re.sub(r'    def _build_page_visuals\(self, specs: List\[VisualSpec\], page: int\) -> List\[dict\]:.*?(?=    # -- Type mappers)', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated _build_page_visuals")

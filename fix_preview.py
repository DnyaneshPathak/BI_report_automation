import sys

file_path = 'src/bi_automation/web/preview_renderer.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_method = '''    def _echarts_option(self, spec: VisualSpec) -> Optional[dict]:
        try:
            import pandas as pd
            ctype = spec.chart_type
            data = spec.data
            
            x_col = spec.dimension or ""
            y_col = spec.measure or ""
            
            agg_label = (spec.aggregation or "").upper() if hasattr(spec, 'aggregation') and spec.aggregation else ""
            if y_col in ("Count", "Frequency"):
                y_axis_name = y_col
            elif y_col:
                y_axis_name = f"{agg_label}({y_col})" if agg_label else y_col
            else:
                y_axis_name = ""

            has_axes = ctype not in ("donut", "treemap", "pie", "map")

            option = {
                "color": CHART_COLORS,
                "tooltip": {"trigger": "axis" if ctype in ("line", "bar", "area", "multi_line") else "item"},
                "series": []
            }
            
            if has_axes:
                option["grid"] = {"left": "15%", "right": "5%", "bottom": "25%", "top": "12%", "containLabel": True}
                option["dataZoom"] = [{"type": "inside"}, {"type": "slider", "height": 20, "bottom": 10}]
                option["xAxis"] = {
                    "name": x_col,
                    "nameLocation": "center",
                    "nameGap": 35,
                    "nameTextStyle": {"fontSize": 11, "fontWeight": "bold"},
                    "axisLabel": {"interval": "auto", "rotate": 45, "hideOverlap": True, "margin": 10, "fontSize": 10},
                    "scale": True
                }
                option["yAxis"] = {
                    "name": y_axis_name,
                    "nameLocation": "middle",
                    "nameRotate": 90,
                    "nameGap": 65,
                    "nameTextStyle": {"fontSize": 11, "fontWeight": "bold"},
                    "axisLabel": {"hideOverlap": True, "fontSize": 10},
                    "scale": True
                }

            if ctype == "line" and data.get("labels"):
                option["xAxis"].update({"type": "category", "data": data["labels"]})
                option["yAxis"].update({"type": "value"})
                option["series"] = [{"data": data["values"], "type": "line", "smooth": True}]
                
            elif ctype == "multi_line" and data:
                labels = list(data.keys())
                if labels and isinstance(data[labels[0]], dict):
                    cat_keys = set()
                    for v in data.values():
                        cat_keys.update(v.keys())
                    cat_list = list(cat_keys)
                    
                    option["legend"] = {"data": cat_list, "bottom": 0}
                    option["xAxis"].update({"type": "category", "data": labels})
                    option["yAxis"].update({"type": "value"})
                    series = []
                    for cat in cat_list:
                        series.append({
                            "name": cat,
                            "type": "line",
                            "data": [data[lbl].get(cat, 0) for lbl in labels]
                        })
                    option["series"] = series

            elif ctype == "bar" and data.get("labels"):
                option["xAxis"].update({"type": "category", "data": data["labels"]})
                option["yAxis"].update({"type": "value"})
                option["series"] = [{"data": data["values"], "type": "bar"}]

            elif ctype == "histogram" and data.get("labels"):
                option["xAxis"].update({"type": "category", "data": data["labels"]})
                option["yAxis"].update({"type": "value"})
                option["series"] = [{"data": data["values"], "type": "bar", "itemStyle": {"color": PALETTE["accent"]}, "barCategoryGap": "0%"}]

            elif ctype == "donut" and data.get("labels"):
                pie_data = [{"name": l, "value": v} for l, v in zip(data["labels"], data["values"])]
                option["xAxis"] = {"show": False}
                option["yAxis"] = {"show": False}
                option["legend"] = {"orient": "vertical", "left": "left"}
                option["series"] = [{
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "data": pie_data
                }]

            elif ctype == "pie" and data.get("labels"):
                pie_data = [{"name": l, "value": v} for l, v in zip(data["labels"], data["values"])]
                option["xAxis"] = {"show": False}
                option["yAxis"] = {"show": False}
                option["legend"] = {"orient": "vertical", "left": "left"}
                option["series"] = [{
                    "type": "pie",
                    "radius": "70%",
                    "data": pie_data
                }]

            elif ctype == "funnel" and data.get("labels"):
                funnel_data = [{"name": l, "value": v} for l, v in zip(data["labels"], data["values"])]
                option["xAxis"] = {"show": False}
                option["yAxis"] = {"show": False}
                option["legend"] = {"orient": "vertical", "left": "left"}
                option["series"] = [{
                    "type": "funnel",
                    "left": "10%",
                    "width": "80%",
                    "data": funnel_data
                }]

            elif ctype == "waterfall" and data.get("labels"):
                option["xAxis"].update({"type": "category", "data": data["labels"]})
                option["yAxis"].update({"type": "value"})
                option["series"] = [{"data": data["values"], "type": "bar"}]

            elif ctype == "treemap" and data.get("labels"):
                tm_data = [{"name": l, "value": v} for l, v in zip(data["labels"], data["values"])]
                option["xAxis"] = {"show": False}
                option["yAxis"] = {"show": False}
                option["series"] = [{
                    "type": "treemap",
                    "data": tm_data,
                    "roam": False
                }]

            elif ctype == "area" and data.get("labels"):
                option["xAxis"].update({"type": "category", "data": data["labels"]})
                option["yAxis"].update({"type": "value"})
                option["series"] = [{
                    "data": data["values"], "type": "line", "smooth": True,
                    "areaStyle": {"opacity": 0.4}
                }]

            elif ctype == "heatmap" and data.get("labels"):
                option["xAxis"].update({"type": "category", "data": data["labels"]})
                option["yAxis"].update({"type": "value"})
                option["series"] = [{"data": data["values"], "type": "bar"}]

            elif ctype == "scatter":
                is_x_cat = False
                if data.get("x") and data.get("y"):
                    scatter_data = list(zip(data["x"], data["y"]))
                elif spec.dimension in self.df.columns and spec.measure in self.df.columns:
                    x_vals = self.df[spec.dimension].dropna()
                    y_vals = self.df[spec.measure].dropna()
                    
                    if not pd.api.types.is_numeric_dtype(x_vals):
                        is_x_cat = True
                        
                    idx = x_vals.index.intersection(y_vals.index)[:1000]
                    if is_x_cat:
                        scatter_data = [[str(x_vals[i]), float(y_vals[i])] for i in idx]
                    else:
                        scatter_data = [[float(x_vals[i]), float(y_vals[i])] for i in idx]
                else:
                    raise KeyError(f"Columns missing for scatter: {spec.dimension}, {spec.measure}")

                if is_x_cat:
                    option["xAxis"].update({"type": "category", "name": x_col})
                else:
                    option["xAxis"].update({"type": "value", "name": x_col})
                    
                option["yAxis"].update({"type": "value", "name": y_col})
                option["series"] = [{
                    "type": "scatter",
                    "data": scatter_data,
                    "symbolSize": 6,
                    "itemStyle": {"opacity": 0.6}
                }]
                
            elif ctype == "stacked_bar" and data:
                labels = list(data.keys())
                if labels and isinstance(data[labels[0]], dict):
                    cat_keys = set()
                    for v in data.values():
                        cat_keys.update(v.keys())
                    cat_list = list(cat_keys)
                    
                    option["legend"] = {"data": cat_list, "bottom": 0}
                    option["xAxis"] = {"type": "category", "data": labels}
                    option["yAxis"] = {"type": "value"}
                    series = []
                    for cat in cat_list:
                        series.append({
                            "name": cat,
                            "type": "bar",
                            "stack": "total",
                            "data": [data[lbl].get(cat, 0) for lbl in labels]
                        })
                    option["series"] = series
            else:
                return None

            return option
        except Exception as e:
            logger.error("Chart render failed for %s: %s", spec.id, e)
            return None
'''
new_lines = lines[:184] + [new_method + '\n'] + lines[434:]
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Replaced lines successfully!")

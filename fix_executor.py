import os
import re

file_path = 'src/bi_automation/engine/executor.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''    def _execute_visual(self, item: Dict[str, Any]) -> Dict[str, Any]:
        # For visual and table, we generally have group_by (or x/series) and metrics (or y)
        group_cols = []
        metrics = []
        
        # Unify visual/table schema mapping
        if item.get("type") == "table":
            group_cols = item.get("group_by", [])
            metrics = item.get("metrics", [])
        else: # visual
            x = item.get("x")
            if x and isinstance(x, dict):
                group_cols.append(x.get("column"))
            elif x and isinstance(x, str):
                group_cols.append(x)
                
            series_col = item.get("series")
            if series_col:
                if isinstance(series_col, dict):
                    group_cols.append(series_col.get("column"))
                else:
                    group_cols.append(series_col)
                    
            y = item.get("y", [])
            if isinstance(y, dict):
                metrics = [y]
            else:
                metrics = y
                
        # Filter valid columns
        group_cols = [c for c in group_cols if c and c in self.df.columns]
        
        if not group_cols and not metrics:
            raise ValueError("No valid grouping or metric columns provided.")
            
        # Handle time grain formatting if applicable (skip for now to keep simple)
            
        # Build agg dict - handling multiple metrics on same col
        # Use pd.NamedAgg for robust aggregation
        agg_kwargs = {}
        metric_col_names = []
        for i, m in enumerate(metrics):
            col = m.get("column")
            agg = m.get("agg", "sum")
            if col and col in self.df.columns:
                pd_agg = "count"
                if agg == "sum": pd_agg = "sum"
                elif agg == "avg": pd_agg = "mean"
                elif agg == "median": pd_agg = "median"
                elif agg == "min": pd_agg = "min"
                elif agg == "max": pd_agg = "max"
                elif agg == "distinct_count": pd_agg = "nunique"
                
                out_col = f"{agg}_{col}"
                agg_kwargs[out_col] = pd.NamedAgg(column=col, aggfunc=pd_agg)
                metric_col_names.append(out_col)
                
        if not group_cols and agg_kwargs:
            # Global aggregation
            grouped = self.df.agg(**{k: (v.column, v.aggfunc) for k, v in agg_kwargs.items()}).to_frame().T
        elif group_cols and agg_kwargs:
            # Group and aggregate
            grouped = self.df.groupby(group_cols, dropna=False).agg(**agg_kwargs).reset_index()
        elif group_cols and not agg_kwargs:
            # Just group (e.g. distinct values)
            grouped = self.df[group_cols].drop_duplicates().reset_index(drop=True)
        else:
            grouped = pd.DataFrame()
        
        # Sort and Top N
        sort_cfg = item.get("sort")
        if sort_cfg:
            sort_by = sort_cfg.get("by")
            sort_dir = sort_cfg.get("dir", "desc")
            if sort_by in grouped.columns:
                grouped = grouped.sort_values(by=sort_by, ascending=(sort_dir == "asc"))
            else:
                # Try prefix search if sorting by just the raw column name
                for c in grouped.columns:
                    if c.endswith(f"_{sort_by}"):
                        grouped = grouped.sort_values(by=c, ascending=(sort_dir == "asc"))
                        break
                
        top_n = item.get("top_n")
        if top_n and isinstance(top_n, int) and top_n > 0:
            grouped = grouped.head(top_n)
            
        # Verify step
        warnings = []
        if grouped.empty:
            warnings.append("Result is empty.")
        elif grouped.isnull().all().all():
            warnings.append("Result contains only null values.")
            
        dataset = {
            "source": [grouped.columns.tolist()] + grouped.replace({np.nan: None}).values.tolist()
        }
        
        return {
            "dataset": dataset,
            "title": item.get("title", ""),
            "chart_type": item.get("chart", "bar") if item.get("type") == "visual" else "table",
            "warnings": warnings
        }
'''

content = re.sub(r'    def _execute_visual\(self, item: Dict\[str, Any\]\) -> Dict\[str, Any\]:.*?(?=\n\Z|\n\w)', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated _execute_visual in executor.py")

import os

file_path = 'src/bi_automation/profiling/profiler.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

schema_card_method = '''
    def generate_schema_card(self, col_stats: Dict[str, ColumnStats], llm_send_sample_labels: bool = False) -> List[Dict[str, Any]]:
        """Generate the Schema Card expected by the LLM Planner."""
        schema_card = []
        for col_name, stats in col_stats.items():
            # Sanitize column name slightly for LLM safety (cap length)
            safe_name = str(col_name)[:80].replace('\\n', ' ').replace('\\r', '')
            
            card = {
                "name": safe_name,
                "role": stats.feature_role,
                "dtype": stats.analytical_type,
                "unique_count": stats.unique_count,
                "null_pct": stats.missing_pct,
            }
            
            if stats.analytical_type in ("continuous", "discrete_numeric"):
                card["numeric_min"] = stats.minimum
                card["numeric_max"] = stats.maximum
                card["numeric_median"] = stats.median
            
            if stats.analytical_type == "datetime":
                card["date_min"] = stats.minimum  # Assuming these were stored as string/timestamp
                card["date_max"] = stats.maximum
                
            if llm_send_sample_labels and stats.analytical_type in ("categorical_nominal", "categorical_ordinal", "binary"):
                if stats.freq_distribution:
                    card["top_5_categories"] = list(stats.freq_distribution.keys())[:5]
                    
            schema_card.append(card)
            
        return schema_card
'''

# Find the end of DataProfiler class and append it there.
content = content + schema_card_method

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Added generate_schema_card to profiler.py")

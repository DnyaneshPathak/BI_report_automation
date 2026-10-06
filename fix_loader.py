import os
import re

file_path = 'src/bi_automation/ingestion/loader.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add preparation_log to WorkbookIngestionResult
content = re.sub(
    r'    warnings: List\[str\] = field\(default_factory=list\)\n',
    '    warnings: List[str] = field(default_factory=list)\n    preparation_log: List[str] = field(default_factory=list)\n',
    content
)

# Modify _clean_dataframe to not drop entirely empty rows/cols, or at least log it
clean_func = '''    def _clean_dataframe(self, df: pd.DataFrame, sheet_name: str, result: WorkbookIngestionResult) -> pd.DataFrame:
        """Basic early-stage normalisation: clean headers, log actions."""
        orig_rows, orig_cols = df.shape
        
        # Clean column names
        def _clean_col_name(c) -> str:
            if pd.isna(c) or str(c).strip() == "":
                return "Unnamed"
            name = str(c).strip()
            name = re.sub(r"\s+", " ", name)
            return name

        new_cols = []
        seen = {}
        for c in df.columns:
            clean = _clean_col_name(c)
            if clean in seen:
                seen[clean] += 1
                clean = f"{clean}_{seen[clean]}"
            else:
                seen[clean] = 0
            new_cols.append(clean)
            
        df.columns = new_cols
        
        # We DO NOT drop any rows or columns to respect the "never mutates values" rule.
        # But we do log the header cleaning.
        if list(df.columns) != new_cols:
            result.preparation_log.append(f"Cleaned column headers in sheet '{sheet_name}'.")
        
        # Type parsing logic for currency/percent can be added here if needed
        # For now, we just rely on pandas to parse basic numeric/date types.
        
        return df
'''

content = re.sub(r'    def _clean_dataframe\(self, df: pd\.DataFrame\) -> pd\.DataFrame:.*?(?=    def _select_primary_sheet)', clean_func, content, flags=re.DOTALL)

# Update calls to _clean_dataframe in _load_csv and _load_excel
content = content.replace('self._clean_dataframe(df)', 'self._clean_dataframe(df, sheet_name, result)')

if content != open(file_path, 'r', encoding='utf-8').read():
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated loader.py")

import os
import re

file_path = 'src/bi_automation/preprocessing/type_detector.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''    def _detect_column(self, col: str, series: pd.Series) -> ColumnProfile:
        profile = ColumnProfile(name=col)
        total = len(series)
        n_unique = series.nunique(dropna=True)
        unique_ratio = n_unique / max(total, 1)

        # 1. Date/time
        if pd.api.types.is_datetime64_any_dtype(series):
            profile.analytical_type = "datetime"
            profile.feature_role    = "date"
            return profile

        # ID Regex Check (ignores value constraints per new rules)
        # Note: we need to ensure it's not a clear measure like "Ticket Price"
        # The prompt says: "A numeric-looking column named 'Ticket No' must be identifier even if values repeat."
        # Remove measure words from ID matches if they have them.
        is_id_name = bool(_ID_PATTERNS.search(col)) and not bool(_FINANCIAL_PATTERNS.search(col))
        
        # Phone
        if re.search(r'\\b(phone|mobile)\\b', col, re.I):
            profile.analytical_type = "categorical_nominal"
            profile.feature_role    = "phone_like"
            return profile

        # Geo
        if bool(_GEO_PATTERNS.search(col)) and bool(re.search(r'\\b(zip|postal|pin)\\b', col, re.I)):
            profile.analytical_type = "categorical_nominal"
            profile.feature_role    = "code_geo"
            return profile

        # 2. Numeric
        if pd.api.types.is_numeric_dtype(series):
            if is_id_name:
                profile.analytical_type = "identifier"
                profile.feature_role    = "identifier"
                return profile
                
            # If unique ratio is 100% and it's integers, probably an ID
            all_int = (series.dropna() % 1 == 0).all() if len(series.dropna()) > 0 else False
            if all_int and unique_ratio > 0.99 and n_unique > 10:
                profile.analytical_type = "identifier"
                profile.feature_role    = "identifier"
                return profile
                
            if _PERCENT_PATTERNS.search(col) or _DURATION_PATTERNS.search(col):
                profile.analytical_type = "continuous"
                profile.feature_role    = "measure_nonadditive"
                return profile
                
            # Assume additive measure by default for numeric
            profile.analytical_type = "continuous"
            profile.feature_role    = "measure_additive"
            return profile

        # 3. Categorical/Text
        str_series = series.dropna().astype(str).str.strip().str.lower()
        
        if is_id_name or (unique_ratio > 0.9 and n_unique > 50):
            profile.analytical_type = "identifier"
            profile.feature_role    = "identifier"
            return profile
            
        if bool(_GEO_PATTERNS.search(col)):
            profile.analytical_type = "categorical_nominal"
            profile.feature_role    = "dimension" # Treating geo as dimension
            return profile
            
        if n_unique <= 50:
            profile.analytical_type = "categorical_nominal"
            profile.feature_role    = "dimension"
            return profile
            
        # High cardinality
        profile.analytical_type = "categorical_nominal"
        profile.feature_role    = "dimension_high_card"
        return profile
'''

content = re.sub(r'    def _detect_column\(self, col: str, series: pd\.Series\) -> ColumnProfile:.*?(?=    def _infer_datetime_grain)', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated type_detector.py")

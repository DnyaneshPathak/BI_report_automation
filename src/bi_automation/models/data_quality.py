from dataclasses import dataclass

@dataclass
class DataQualitySummary:
    total_rows: int = 0
    total_columns: int = 0
    missing_cells: int = 0
    missing_percentage: float = 0.0
    duplicate_rows: int = 0
    duplicate_percentage: float = 0.0
    outlier_count: int = 0
    numeric_count: int = 0
    categorical_count: int = 0
    date_count: int = 0
    identifier_count: int = 0

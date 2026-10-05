from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class ColumnDef:
    name: str
    data_type: str  # string, int64, double, dateTime
    is_hidden: bool = False
    format_string: Optional[str] = None
    summarize_by: str = "none"

@dataclass
class MeasureDef:
    name: str
    expression: str
    format_string: Optional[str] = None
    display_folder: Optional[str] = None
    is_hidden: bool = False

@dataclass
class TableDef:
    name: str
    columns: List[ColumnDef] = field(default_factory=list)
    measures: List[MeasureDef] = field(default_factory=list)
    is_hidden: bool = False

@dataclass
class RelationshipDef:
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    cross_filtering_behavior: str = "bothDirections"  # oneDirection, bothDirections
    is_active: bool = True

@dataclass
class SemanticModel:
    tables: List[TableDef] = field(default_factory=list)
    relationships: List[RelationshipDef] = field(default_factory=list)
    culture: str = "en-US"

class SemanticModelBuilder:
    """
    Phase 6: Builds the abstract Semantic Model (Tables, Relationships, Measures).
    """
    def __init__(self, df_schema: Dict[str, str], table_name: str = "FactData"):
        self.df_schema = df_schema
        self.table_name = table_name
        self.model = SemanticModel()

    def _map_dtype(self, pd_type: str) -> str:
        pd_type = str(pd_type).lower()
        if "int" in pd_type: return "int64"
        if "float" in pd_type: return "double"
        if "datetime" in pd_type: return "dateTime"
        if "bool" in pd_type: return "boolean"
        return "string"

    def build(self) -> SemanticModel:
        # Create fact table
        fact_table = TableDef(name=self.table_name)
        for col, dtype in self.df_schema.items():
            dt = self._map_dtype(dtype)
            summ = "sum" if dt in ("int64", "double") else "none"
            fact_table.columns.append(ColumnDef(
                name=col,
                data_type=dt,
                summarize_by=summ
            ))
        
        # In a full star-schema, we would extract dimension tables and add relationships.
        # For a flat dataset, we just use the fact table.
        self.model.tables.append(fact_table)
        return self.model

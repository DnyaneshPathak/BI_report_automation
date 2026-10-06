from typing import Dict, Any, List


class ValidationError(Exception):
    pass


class PlanValidator:
    """Deterministic rule-based validator for the LLM's plan."""

    ALLOWED_AGGS = {
        "identifier": {"count_rows", "distinct_count", "count_non_null", "none"},
        "code_geo": {"count_rows", "distinct_count", "none"},
        "phone_like": {"count_rows", "distinct_count", "none"},
        "measure_additive": {"sum", "avg", "median", "min", "max", "count_non_null", "none"},
        "measure_nonadditive": {"avg", "median", "min", "max", "none"},
        "dimension": {"count_rows", "distinct_count", "pct_of_total", "none"},
        "dimension_high_card": {"count_rows", "distinct_count", "pct_of_total", "none"},
        "date": {"min", "max", "count_rows", "distinct_count", "none"},
        "datetime": {"min", "max", "count_rows", "distinct_count", "none"},
        "text_free": {"count_non_null", "count_rows", "none"},
        "constant": {"count_rows", "none"},
    }

    # Map real-world feature_role values (from profiler/type_detector) to ALLOWED_AGGS keys.
    # Keys are lowercased for case-insensitive matching.
    ROLE_NORMALIZE_MAP = {
        "identifier": "identifier",
        "measure": "measure_additive",
        "financial measure": "measure_additive",
        "target-like metric": "measure_additive",
        "quantity": "measure_additive",
        "measure_additive": "measure_additive",
        "measure_nonadditive": "measure_nonadditive",
        "dimension": "dimension",
        "dimension_high_card": "dimension_high_card",
        "code_geo": "code_geo",
        "phone_like": "phone_like",
        "date": "date",
        "datetime": "datetime",
        "text_free": "text_free",
        "constant": "constant",
        "location": "dimension",
        "status": "dimension",
        "binary": "dimension",
    }

    def __init__(self, schema_card: List[Dict[str, Any]]):
        self.schema_card = schema_card
        self.columns = {col["name"]: col for col in schema_card}

    def _normalize_role(self, role: str) -> str:
        """Normalize mixed-case feature role string to a canonical ALLOWED_AGGS key."""
        return self.ROLE_NORMALIZE_MAP.get(role.lower().strip(), "dimension")

    def validate(self, plan: Dict[str, Any]) -> List[str]:
        """
        Validates the plan.
        Returns a list of error strings (empty if valid).
        """
        errors = []

        if plan.get("needs_clarification"):
            return []  # No items expected

        items = plan.get("items", [])

        for idx, item in enumerate(items):
            try:
                self._validate_item(item)
            except ValidationError as e:
                errors.append(f"Item {item.get('id', idx)} error: {str(e)}")

        return errors

    def _validate_item(self, item: Dict[str, Any]):
        # Validate X axis column exists
        if "x" in item and item["x"]:
            col = item["x"]["column"]
            if col not in self.columns:
                raise ValidationError(f"Column '{col}' does not exist in schema.")

        # Collect all metrics from y / metrics / metric fields
        metrics = []
        if "y" in item and item["y"]:
            metrics.extend(item["y"])
        if "metrics" in item and item["metrics"]:
            metrics.extend(item["metrics"])
        if "metric" in item and item["metric"]:
            metrics.append(item["metric"])

        for m in metrics:
            col = m["column"]
            agg = m["agg"]
            if col not in self.columns:
                raise ValidationError(f"Column '{col}' does not exist in schema.")

            # Normalize the feature_role from the schema card and look up allowed aggs
            raw_role = self.columns[col].get("role", "dimension")
            normalized_role = self._normalize_role(raw_role)
            allowed = self.ALLOWED_AGGS.get(normalized_role, {"count_rows", "none"})
            if agg not in allowed:
                raise ValidationError(
                    f"E_AGG_NOT_ALLOWED: Column '{col}' has role '{raw_role}' "
                    f"(normalized: '{normalized_role}'); allowed: {', '.join(sorted(allowed))}."
                )

        # Validate series and group_by columns exist
        groups = []
        if "series" in item and item["series"]:
            groups.append(item["series"]["column"])
        if "group_by" in item and item["group_by"]:
            groups.extend(item["group_by"])

        for col in groups:
            if col not in self.columns:
                raise ValidationError(f"Column '{col}' does not exist in schema.")

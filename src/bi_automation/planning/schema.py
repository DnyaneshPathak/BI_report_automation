from typing import Dict, Any

PLANNER_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "version": {"type": "integer", "const": 1},
        "needs_clarification": {
            "type": ["string", "null"],
            "description": "If the prompt is completely ambiguous or impossible, put a clarifying question here."
        },
        "requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "text": {"type": "string"}
                },
                "required": ["id", "text"],
                "additionalProperties": False
            }
        },
        "filters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "column": {"type": "string"},
                    "op": {"type": "string", "enum": ["eq", "neq", "gt", "lt", "between", "in", "like"]},
                    "value": {},
                    "from": {"type": "string"}
                },
                "required": ["column", "op", "value", "from"],
                "additionalProperties": False
            }
        },
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "requirement": {"type": "string"},
                    "type": {"type": "string", "enum": ["visual", "kpi", "table", "matrix", "slicer", "text"]},
                    "chart": {"type": "string"},
                    "x": {
                        "type": ["object", "null"],
                        "properties": {
                            "column": {"type": "string"},
                            "grain": {"type": ["string", "null"]}
                        },
                        "required": ["column"],
                        "additionalProperties": False
                    },
                    "y": {
                        "type": ["array", "null"],
                        "items": {
                            "type": "object",
                            "properties": {
                                "column": {"type": "string"},
                                "agg": {"type": "string"}
                            },
                            "required": ["column", "agg"],
                            "additionalProperties": False
                        }
                    },
                    "series": {
                        "type": ["object", "null"],
                        "properties": {
                            "column": {"type": "string"}
                        },
                        "required": ["column"],
                        "additionalProperties": False
                    },
                    "group_by": {
                        "type": ["array", "null"],
                        "items": {"type": "string"}
                    },
                    "metrics": {
                        "type": ["array", "null"],
                        "items": {
                            "type": "object",
                            "properties": {
                                "column": {"type": "string"},
                                "agg": {"type": "string"}
                            },
                            "required": ["column", "agg"],
                            "additionalProperties": False
                        }
                    },
                    "metric": {
                        "type": ["object", "null"],
                        "properties": {
                            "column": {"type": "string"},
                            "agg": {"type": "string"}
                        },
                        "required": ["column", "agg"],
                        "additionalProperties": False
                    },
                    "sort": {
                        "type": ["object", "null"],
                        "properties": {
                            "by": {"type": "string"},
                            "dir": {"type": "string", "enum": ["asc", "desc"]}
                        },
                        "required": ["by", "dir"],
                        "additionalProperties": False
                    },
                    "top_n": {"type": ["integer", "null"]},
                    "title": {"type": "string"},
                    "dynamic": {
                        "type": ["object", "null"],
                        "properties": {
                            "time_grain": {"type": "array", "items": {"type": "string"}},
                            "default_grain": {"type": "string"}
                        },
                        "required": ["time_grain", "default_grain"],
                        "additionalProperties": False
                    },
                    "totals": {"type": ["boolean", "null"]},
                    "confidence": {"type": "number"}
                },
                "required": ["id", "requirement", "type", "title", "confidence"],
                "additionalProperties": False
            },
            "maxItems": 40
        },
        "assumptions": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["version", "needs_clarification", "requirements", "filters", "items", "assumptions"],
    "additionalProperties": False
}

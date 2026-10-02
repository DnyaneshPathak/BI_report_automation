"""
src/bi_automation/config/palette.py
Corporate colour palette and chart colour schemes.
"""

PALETTE = {
    "primary"       : "#1B2A4A",   # dark navy
    "secondary"     : "#2563EB",   # blue
    "accent"        : "#3B82F6",
    "background"    : "#F8FAFC",
    "surface"       : "#FFFFFF",
    "border"        : "#E2E8F0",
    "text_primary"  : "#0F172A",
    "text_secondary": "#64748B",
    "success"       : "#059669",
    "warning"       : "#D97706",
    "danger"        : "#DC2626",
}

# 10-colour categorical palette (colour-blind safe)
CHART_COLORS = [
    "#2563EB", "#059669", "#D97706", "#7C3AED",
    "#DB2777", "#0891B2", "#EA580C", "#65A30D",
    "#DC2626", "#6366F1",
]

# Sequential (low → high magnitude)
SEQUENTIAL_COLORS = ["#EFF6FF", "#BFDBFE", "#60A5FA", "#2563EB", "#1D4ED8", "#1E3A8A"]

# Diverging (negative → zero → positive)
DIVERGING_COLORS  = ["#DC2626", "#FCA5A5", "#FEF2F2", "#EFF6FF", "#93C5FD", "#2563EB"]

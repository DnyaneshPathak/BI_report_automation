def estimate_text_width(text: str, font_size: int = 12) -> float:
    """Estimate pixel width of a string (approx 0.6 chars per px for average fonts)."""
    if not text:
        return 0.0
    return len(str(text)) * font_size * 0.6

def compute_grid_margins(x_labels: list, y_title: str = "", x_title: str = "", font_size: int = 12) -> dict:
    """
    Dynamically compute ECharts grid margins to prevent label overlap.
    Returns a dict with bottom and left padding, and rotation angle.
    """
    # Left margin: driven by y-axis title
    left_padding = 60 # base for ticks
    if y_title:
        left_padding += font_size * 2 # Space for rotated y-axis title
        
    # Bottom margin: driven by longest x_label and rotation
    max_label_width = max([estimate_text_width(str(lbl), font_size) for lbl in x_labels]) if x_labels else 0
    
    rotate = 0
    if max_label_width > 60 and len(x_labels) > 5:
        rotate = 45
        bottom_padding = (max_label_width * 0.707) + 20 # sin(45) ~ 0.707
    else:
        bottom_padding = font_size * 2
        
    if x_title:
        bottom_padding += font_size * 2 # Space for x-axis title
        
    return {
        "grid": {
            "left": f"{int(left_padding)}px",
            "bottom": f"{int(bottom_padding)}px",
            "right": "30px",
            "top": "40px",
            "containLabel": True
        },
        "xAxis_rotate": rotate
    }

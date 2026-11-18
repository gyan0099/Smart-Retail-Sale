"""
Smart Retail Sales Analytics & Visualization System
UI KPI Cards & Metric Badges
Renders enterprise-styled HTML KPI cards with delta badges and typography.
"""

from typing import Optional

def render_kpi_card(
    title: str, 
    value: str, 
    delta: Optional[str] = None, 
    delta_type: str = "positive", # 'positive', 'negative', 'neutral'
    color_accent: str = "blue", # 'blue', 'green', 'amber', 'purple', 'teal', 'rose'
    subtext: str = ""
) -> str:
    """Returns HTML for a single KPI card."""
    delta_html = ""
    if delta is not None:
        delta_class = f"delta-{delta_type}"
        icon = "▲" if delta_type == "positive" else ("▼" if delta_type == "negative" else "●")
        delta_html = f'<div class="kpi-delta {delta_class}">{icon} {delta}</div>'

    subtext_html = f'<div style="font-size: 11px; color: #94A3B8; margin-top: 4px;">{subtext}</div>' if subtext else ""

    return f"""
    <div class="kpi-card kpi-{color_accent}">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
        {subtext_html}
    </div>
    """

def format_currency(val: float) -> str:
    """Formats numeric values into Indian Rupee (₹) standard notation with Lakhs / Crores / K / M."""
    if abs(val) >= 10_000_000:
        return f"₹{val / 10_000_000:.2f} Cr"
    elif abs(val) >= 100_000:
        return f"₹{val / 100_000:.2f} L"
    elif abs(val) >= 1_000:
        return f"₹{val / 1_000:.1f} K"
    else:
        return f"₹{val:,.2f}"

def format_number(val: int or float) -> str:
    """Formats large integer counts."""
    if abs(val) >= 1_000_000:
        return f"{val / 1_000_000:.2f}M"
    elif abs(val) >= 1_000:
        return f"{val / 1_000:.1f}K"
    else:
        return f"{val:,}"

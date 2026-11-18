"""
Smart Retail Sales Analytics & Visualization System
Sidebar Component: Navigation & Global Filter Controls
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Tuple, Dict, Any

MODULE_PAGES = [
    "🏠 Executive Dashboard",
    "📈 Sales Analytics",
    "📦 Product Analytics",
    "👥 Customer Analytics",
    "🗺️ Regional Analytics",
    "💰 Profit Analytics",
    "🤖 Machine Learning",
    "📁 Data Management",
    "📊 Advanced Visualizations",
    "📑 Reports & Business Insights",
    "🎓 Academic Report (SR University)"
]

def render_sidebar(df: pd.DataFrame) -> Tuple[str, pd.DataFrame, Dict[str, Any]]:
    """
    Renders sidebar navigation, filter widgets, and returns:
    - selected_page: str
    - filtered_df: pd.DataFrame
    - filter_state: dict
    """
    st.sidebar.markdown("""
        <div style="text-align: center; padding: 12px 0 20px 0;">
            <div style="background: linear-gradient(135deg, #1E3A8A, #3B82F6); color: white; border-radius: 12px; padding: 12px; margin-bottom: 8px;">
                <h3 style="margin: 0; font-size: 18px; color: white;">🛒 SMART RETAIL</h3>
                <div style="font-size: 11px; opacity: 0.85; margin-top: 2px;">Analytics & BI System</div>
            </div>
            <div style="font-size: 11px; color: #64748B; font-weight: 500;">SR University • DAV Project</div>
        </div>
    """, unsafe_allow_html=True)

    # 1. Navigation Menu
    selected_page = st.sidebar.radio(
        "Navigation Menu",
        MODULE_PAGES,
        index=0,
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Global Data Filters")

    if df.empty:
        return selected_page, df, {}

    # Prepare filter choices
    df_filtered = df.copy()

    # 2. Date Range Filter
    if "Order Date" in df.columns:
        df["_parsed_date"] = pd.to_datetime(df["Order Date"], errors="coerce")
        min_date = df["_parsed_date"].min().date() if not df["_parsed_date"].isnull().all() else datetime(2024, 1, 1).date()
        max_date = df["_parsed_date"].max().date() if not df["_parsed_date"].isnull().all() else datetime(2026, 11, 10).date()

        date_selection = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        if isinstance(date_selection, tuple) and len(date_selection) == 2:
            start_d, end_d = date_selection
            df_filtered = df_filtered[
                (pd.to_datetime(df_filtered["Order Date"]).dt.date >= start_d) & 
                (pd.to_datetime(df_filtered["Order Date"]).dt.date <= end_d)
            ]

    # 3. Category Filter
    selected_categories = []
    if "Category" in df.columns:
        categories = sorted(list(df["Category"].dropna().unique()))
        selected_categories = st.sidebar.multiselect(
            "Product Categories",
            options=categories,
            default=categories
        )
        if selected_categories:
            df_filtered = df_filtered[df_filtered["Category"].isin(selected_categories)]

    # 4. Region Filter
    selected_regions = []
    if "Region" in df.columns:
        regions = sorted(list(df["Region"].dropna().unique()))
        selected_regions = st.sidebar.multiselect(
            "Geographic Regions",
            options=regions,
            default=regions
        )
        if selected_regions:
            df_filtered = df_filtered[df_filtered["Region"].isin(selected_regions)]

    # 5. Customer Segment Filter
    selected_segments = []
    if "Customer Segment" in df.columns:
        segments = sorted(list(df["Customer Segment"].dropna().unique()))
        selected_segments = st.sidebar.multiselect(
            "Customer Segment",
            options=segments,
            default=segments
        )
        if selected_segments:
            df_filtered = df_filtered[df_filtered["Customer Segment"].isin(selected_segments)]

    # 6. Payment Method Filter
    selected_payments = []
    if "Payment Method" in df.columns:
        payments = sorted(list(df["Payment Method"].dropna().unique()))
        selected_payments = st.sidebar.multiselect(
            "Payment Method",
            options=payments,
            default=payments
        )
        if selected_payments:
            df_filtered = df_filtered[df_filtered["Payment Method"].isin(selected_payments)]

    # Active Filter Summary
    active_rows = len(df_filtered)
    total_rows = len(df)
    filter_pct = (active_rows / total_rows * 100) if total_rows > 0 else 0

    st.sidebar.markdown(f"""
        <div style="background: #F1F5F9; border-radius: 8px; padding: 10px; margin-top: 15px; font-size: 12px; color: #475569;">
            <b>Active Records:</b> {active_rows:,} / {total_rows:,} ({filter_pct:.1f}%)
        </div>
    """, unsafe_allow_html=True)

    filter_state = {
        "active_rows": active_rows,
        "total_rows": total_rows,
        "categories": selected_categories,
        "regions": selected_regions,
        "segments": selected_segments,
        "payments": selected_payments
    }

    return selected_page, df_filtered, filter_state

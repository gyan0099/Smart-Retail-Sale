"""
Smart Retail Sales Analytics & Multi-Store BI System
Enterprise Multi-Region Retail Operations, Data Cleaning Lab, Interactive Maps & Predictive Analytics
Designed for Data Analytics and Visualization (25CAI202PC201) - SR University
"""

import glob
import io
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import urlparse

import requests

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st

# Configure Streamlit Page
st.set_page_config(
    page_title="Smart Retail Sales Analytics & Store Network",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

sns.set_theme(style="whitegrid")

# Ensure base directory is in sys.path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from config import (
    APP_TITLE, APP_SUBTITLE, COURSE_NAME, INSTITUTION, ACADEMIC_YEAR, 
    ASSETS_DIR, TEMPLATES_DIR, DATA_DIR, INDIAN_STORES_INFO, 
    REGION_COLORS, STORE_TYPE_COLORS
)
from database.db_manager import db_manager
from components.ui_cards import render_kpi_card, format_currency, format_number
from components.visualizer import ChartVisualizer, REGION_COLORS, STORE_TYPE_COLORS

# Analytics Engines
from analytics.executive_analytics import ExecutiveAnalytics
from analytics.sales_analytics import SalesAnalytics
from analytics.product_analytics import ProductAnalytics
from analytics.customer_analytics import CustomerAnalytics
from analytics.regional_analytics import RegionalAnalytics
from analytics.profit_analytics import ProfitAnalytics

# Machine Learning
from machine_learning.forecasting import SalesForecaster
from machine_learning.demand_prediction import DemandPredictor
from machine_learning.customer_clustering import CustomerClusterer

# Reports & Insights
from reports.excel_exporter import ExcelReportExporter
from reports.pdf_exporter import PDFReportExporter
from reports.insights_generator import InsightsGenerator

# Load Custom CSS
css_file = os.path.join(ASSETS_DIR, "style.css")
if os.path.exists(css_file):
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ==============================================================================
# Helper Functions for Data Cleaning Lab
# ==============================================================================

def default_strategy(df, col):
    """Smart default strategy per column type."""
    if col.endswith("_at") or "date" in col.lower():
        return "leave as is"
    return "median" if pd.api.types.is_numeric_dtype(df[col]) else "mode"


def clean_dataframe(df, strategies, constants, remove_duplicates=True):
    """
    Cleans DataFrame according to selected strategies per column and eliminates duplicate rows.
    Returns (cleaned_df, log_df) where log_df lists every single changed cell or dropped row.
    """
    cleaned = df.copy()
    log, drop_idx = [], set()
    id_cols = [c for c in ("Order ID", "Store Name", "City", "Customer Name", "Product Name", "Category") if c in df.columns]

    # 1. Deduplication: Detect and record duplicate transactions
    if remove_duplicates:
        dup_subset = ["Order ID"] if "Order ID" in df.columns else None
        dup_mask = df.duplicated(subset=dup_subset, keep="first")
        for idx in df.index[dup_mask]:
            drop_idx.add(idx)
            entry = {
                "row_index": idx,
                "csv_line_number": idx + 2,
                "column": "Order ID" if "Order ID" in df.columns else "All Columns",
                "old_value": f"Duplicate Order ({df.at[idx, 'Order ID'] if 'Order ID' in df.columns else 'Row'})",
                "method": "drop duplicate row",
                "new_value": "(row deleted)"
            }
            for c in id_cols:
                entry[c] = df.at[idx, c] if c in df.columns else ""
            log.append(entry)

    # 2. Missing Value Imputation or Row Dropping
    for col, strat in strategies.items():
        mask = df[col].isna()
        if not mask.any() or strat == "leave as is":
            continue

        if strat == "drop rows":
            for idx in df.index[mask]:
                drop_idx.add(idx)
                entry = {
                    "row_index": idx,
                    "csv_line_number": idx + 2,
                    "column": col,
                    "old_value": "(empty)",
                    "method": "drop row (missing value)",
                    "new_value": "(row deleted)"
                }
                for c in id_cols:
                    entry[c] = df.at[idx, c] if c in df.columns else ""
                log.append(entry)
        else:
            numeric = pd.api.types.is_numeric_dtype(df[col])
            if strat == "mean":
                val = df[col].mean()
            elif strat == "median":
                val = df[col].median()
            elif strat == "mode":
                m = df[col].mode(dropna=True)
                val = m.iloc[0] if len(m) else np.nan
            elif strat == "zero":
                val = 0
            else:  # constant
                val = constants.get(col, "")
                if numeric:
                    try:
                        val = float(val)
                    except ValueError:
                        val = np.nan
            if pd.isna(val):
                continue
            cleaned.loc[mask, col] = val
            fill_txt = round(float(val), 4) if isinstance(val, (int, float, np.number)) else val

            for idx in df.index[mask]:
                entry = {
                    "row_index": idx,
                    "csv_line_number": idx + 2,
                    "column": col,
                    "old_value": "(empty)",
                    "method": strat,
                    "new_value": fill_txt
                }
                for c in id_cols:
                    entry[c] = df.at[idx, c] if c in df.columns else ""
                log.append(entry)

    # Delete all identified duplicate and corrupted rows
    cleaned = cleaned.drop(index=list(drop_idx)).reset_index(drop=True)
    
    # Recalculate derivative columns if present
    if "Quantity" in cleaned.columns and "Unit Price" in cleaned.columns:
        disc = cleaned["Discount"] if "Discount" in cleaned.columns else 0.0
        cleaned["Revenue"] = (cleaned["Quantity"] * cleaned["Unit Price"] * (1 - disc)).round(2)
    if "Quantity" in cleaned.columns and "Unit Cost" in cleaned.columns:
        cleaned["Cost"] = (cleaned["Quantity"] * cleaned["Unit Cost"]).round(2)
    if "Revenue" in cleaned.columns and "Cost" in cleaned.columns:
        cleaned["Profit"] = (cleaned["Revenue"] - cleaned["Cost"]).round(2)
        cleaned["Profit Margin"] = np.where(cleaned["Revenue"] > 0, ((cleaned["Profit"] / cleaned["Revenue"]) * 100).round(2), 0.0)

    # Attach coordinates if missing
    if "City" in cleaned.columns:
        if "Latitude" not in cleaned.columns or cleaned["Latitude"].isnull().all():
            cleaned["Latitude"] = cleaned["City"].map(lambda c: INDIAN_STORES_INFO.get(c, {}).get("lat", np.nan))
            cleaned["Longitude"] = cleaned["City"].map(lambda c: INDIAN_STORES_INFO.get(c, {}).get("lon", np.nan))
        if "Store Name" not in cleaned.columns or cleaned["Store Name"].isnull().all():
            cleaned["Store Name"] = cleaned["City"].map(lambda c: INDIAN_STORES_INFO.get(c, {}).get("store_name", f"{c} Retail Outlet"))
        if "Region" not in cleaned.columns or cleaned["Region"].isnull().all():
            cleaned["Region"] = cleaned["City"].map(lambda c: INDIAN_STORES_INFO.get(c, {}).get("region", "South"))

    log_df = pd.DataFrame(log)
    if not log_df.empty:
        first = ["csv_line_number", "row_index"] + [c for c in id_cols] + ["column", "old_value", "method", "new_value"]
        first_valid = [c for c in first if c in log_df.columns]
        log_df = log_df[first_valid].sort_values(["column", "row_index"]).reset_index(drop=True)
        
    return cleaned, log_df


def highlight(df_view, mask_view, color):
    """Styles cells that match mask_view with the given background color."""
    styles = pd.DataFrame(
        np.where(mask_view.values, f"background-color: {color}; color: black; font-weight: bold", ""),
        index=df_view.index, columns=df_view.columns
    )
    return df_view.style.apply(lambda _: styles, axis=None)


# ==============================================================================
# Global State Management
# ==============================================================================

if "active_cleaned_df" not in st.session_state:
    sample_path = os.path.join(DATA_DIR, "retail_sales_sample.csv")
    if os.path.exists(sample_path):
        st.session_state.active_cleaned_df = pd.read_csv(sample_path)
    else:
        from data.sample_generator import generate_retail_dataset
        st.session_state.active_cleaned_df = generate_retail_dataset(3650)
    st.session_state.active_dataset_name = "smart_retail_sales_dataset.csv"

# Header Banner
st.markdown(f"""
    <div class="main-header">
        <div>
            <h1>🛒 {APP_TITLE}</h1>
            <p>{APP_SUBTITLE} • {COURSE_NAME} • {INSTITUTION}</p>
        </div>
        <div class="academic-badge">
            AY {ACADEMIC_YEAR} • SR University
        </div>
    </div>
""", unsafe_allow_html=True)


# ==============================================================================
# Sidebar Data Ingestion & Controls
# ==============================================================================

with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 4px 0 14px 0;">
            <div style="background: linear-gradient(135deg, #1E3A8A, #2563EB); color: white; border-radius: 12px; padding: 12px; margin-bottom: 8px;">
                <h3 style="margin: 0; font-size: 16.5px; color: white;">🛒 SMART RETAIL</h3>
                <div style="font-size: 11px; opacity: 0.9;">Multi-Region Chain BI System</div>
            </div>
            <div style="font-size: 11px; color: #64748B; font-weight: 500;">SR University • DAV Project</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📥 Select or Upload Retail Data")
    data_source_mode = st.radio(
        "Choose Input Mode",
        ["Upload a CSV file", "Fetch from API / CSV URL", "Pick from saved raw files in ./data"],
        index=0,
    )

    df_raw = None
    fname = "retail_sales_raw"

    if data_source_mode == "Fetch from API / CSV URL":
        st.caption("Connect a public CSV URL (for example, a GitHub raw CSV link) or a REST API that returns JSON records.")
        source_url = st.text_input(
            "Dataset URL / API endpoint",
            placeholder="https://raw.githubusercontent.com/username/repository/main/retail_sales.csv",
            key="retail_api_source_url",
        )
        source_format = st.radio("Response format", ["Auto-detect / CSV", "JSON records"], horizontal=True, key="retail_api_format")
        if st.button("🌐 Fetch Data", type="primary", use_container_width=True, key="fetch_retail_api"):
            parsed = urlparse(source_url.strip())
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                st.error("Enter a valid public HTTP or HTTPS URL.")
            else:
                try:
                    response = requests.get(source_url.strip(), timeout=30, headers={"User-Agent": "SmartRetailSalesAnalytics/1.0"})
                    response.raise_for_status()
                    if len(response.content) > 50 * 1024 * 1024:
                        raise ValueError("The response is larger than 50 MB. Please use a smaller dataset.")
                    content_type = response.headers.get("Content-Type", "").lower()
                    if source_format == "JSON records" or "json" in content_type:
                        payload = response.json()
                        if isinstance(payload, list):
                            records = payload
                        elif isinstance(payload, dict):
                            records = next((payload[k] for k in ("data", "results", "records", "items") if isinstance(payload.get(k), list)), None)
                            if records is None:
                                raise ValueError("JSON must contain a list of records, either at the root or under data/results/records/items.")
                        else:
                            raise ValueError("Unsupported JSON response. Expected a list of records.")
                        fetched_df = pd.json_normalize(records)
                    else:
                        fetched_df = pd.read_csv(io.BytesIO(response.content))
                    if fetched_df.empty or len(fetched_df.columns) == 0:
                        raise ValueError("The source returned an empty dataset.")
                    st.session_state["api_fetched_raw_df"] = fetched_df
                    source_name = os.path.splitext(os.path.basename(parsed.path.rstrip("/")))[0] or "api_retail_sales"
                    st.session_state["api_fetched_name"] = re.sub(r"[^A-Za-z0-9_-]+", "_", source_name)[:60]
                    st.session_state["api_fetched_url"] = source_url.strip()
                    st.success(f"Fetched {len(fetched_df):,} rows and {len(fetched_df.columns):,} columns successfully.")
                except requests.exceptions.RequestException as e:
                    st.error(f"API / URL request failed: {e}")
                except Exception as e:
                    st.error(f"Could not read dataset: {e}")

        if "api_fetched_raw_df" in st.session_state:
            df_raw = st.session_state["api_fetched_raw_df"].copy()
            fname = st.session_state.get("api_fetched_name", "api_retail_sales")
            st.caption(f"Source: {st.session_state.get('api_fetched_url', 'API')} • fetched data is treated as raw input until you clean it.")
            st.dataframe(df_raw.head(10), use_container_width=True)
            st.download_button(
                "⬇️ Download fetched raw CSV",
                data=df_raw.to_csv(index=False).encode("utf-8"),
                file_name=f"raw_{fname}.csv",
                mime="text/csv",
                use_container_width=True,
            )
            if st.button("💾 Save fetched data to project ./data folder", use_container_width=True):
                safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", fname)[:60]
                save_path = os.path.join(DATA_DIR, f"raw_{safe_name}.csv")
                df_raw.to_csv(save_path, index=False)
                st.success(f"Saved raw dataset: {save_path}")

    elif data_source_mode == "Upload a CSV file":
        uploaded_file = st.file_uploader("Upload Custom Retail CSV", type=["csv"])
        if uploaded_file is not None:
            try:
                df_raw = pd.read_csv(uploaded_file)
                fname = os.path.splitext(uploaded_file.name)[0]
                st.success(f"✓ Active Upload: **{uploaded_file.name}** ({len(df_raw):,} records)")
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
        else:
            # Automatic Ingestion: Auto-load the real raw multi-store dataset immediately
            if "loaded_file" not in st.session_state:
                st.session_state["loaded_file"] = os.path.join(BASE_DIR, "smart_retail_sales_raw_for_cleaning_lab.csv")

            demo_path = st.session_state.get("loaded_file")
            if os.path.exists(demo_path):
                df_raw = pd.read_csv(demo_path)
                fname = os.path.splitext(os.path.basename(demo_path))[0]
            
            st.success(f"⚡ **Auto-Loaded:** `{fname}.csv` ({len(df_raw):,} records)")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("📊 Clean (3,650)", use_container_width=True):
                    clean_path = os.path.join(BASE_DIR, "smart_retail_sales_dataset.csv")
                    st.session_state["loaded_file"] = clean_path
                    st.session_state.active_cleaned_df = pd.read_csv(clean_path)
                    st.session_state.active_dataset_name = "smart_retail_sales_dataset.csv"
                    st.rerun()
            with col_b2:
                if st.button("🧹 Raw (3,685)", use_container_width=True):
                    raw_path = os.path.join(BASE_DIR, "smart_retail_sales_raw_for_cleaning_lab.csv")
                    st.session_state["loaded_file"] = raw_path
                    st.rerun()

            st.caption("ℹ️ **Data Source:** Project-provided sample dataset generated using a custom Python data generator. Upload or fetch an external dataset to analyse a different source.")

        if "loaded_file" in st.session_state and df_raw is None:
            if os.path.exists(st.session_state["loaded_file"]):
                df_raw = pd.read_csv(st.session_state["loaded_file"])
                fname = os.path.splitext(os.path.basename(st.session_state["loaded_file"]))[0]

    else:
        files = sorted(glob.glob(os.path.join(DATA_DIR, "*.csv")))
        if files:
            choice = st.selectbox("Select CSV file", files, index=0)
            df_raw = pd.read_csv(choice)
            fname = os.path.basename(choice).replace(".csv", "")
        else:
            st.warning("No CSV files found in `./data/` folder.")

    st.markdown("---")
    st.markdown("### 🔍 Global Filter Controls")
    
    # Active dataset
    active_df = st.session_state.active_cleaned_df
    filtered_df = active_df.copy()

    # Region Filter
    if "Region" in active_df.columns:
        regions = sorted(list(active_df["Region"].dropna().unique()))
        sel_regions = st.multiselect("Filter by Region", regions, default=regions)
        if sel_regions:
            filtered_df = filtered_df[filtered_df["Region"].isin(sel_regions)]

    # Store Filter
    store_col = "Store Name" if "Store Name" in active_df.columns else "City"
    if store_col in active_df.columns:
        stores = sorted(list(active_df[store_col].dropna().unique()))
        sel_stores = st.multiselect("Filter by Store / Shop", stores, default=stores)
        if sel_stores:
            filtered_df = filtered_df[filtered_df[store_col].isin(sel_stores)]

    # Category Filter
    if "Category" in active_df.columns:
        cats = sorted(list(active_df["Category"].dropna().unique()))
        sel_cats = st.multiselect("Filter by Category", cats, default=cats)
        if sel_cats:
            filtered_df = filtered_df[filtered_df["Category"].isin(sel_cats)]

    st.caption(f"Active Records: **{len(filtered_df):,}** / **{len(active_df):,}**")


# ==============================================================================
# MAIN TABS ARCHITECTURE
# ==============================================================================

tab_map, tab_dash, tab_clean, tab_cmp, tab_ml, tab_raw_files, tab_reports, tab_academic = st.tabs([
    "🗺️ 1. India & World Store Map",
    "📊 2. Executive BI Dashboard",
    "🧹 3. Data Cleaning Lab",
    "⚖️ 4. Regional Comparisons",
    "🤖 5. Machine Learning Lab",
    "📁 6. Raw & Clean Data Files",
    "📑 7. Reports & Strategic Insights",
    "🎓 8. Academic Report (SR University)"
])


# ==============================================================================
# TAB 1: INDIA & WORLD REGIONAL STORE SALES REPORT (MAIN USER OBJECTIVE)
# ==============================================================================
with tab_map:
    st.subheader("🗺️ India Multi-Region Retail Store Network & GIS Analytics")
    st.caption("Track physical retail store locations across India, regional performance benchmarks, sales volumes, and profit margins.")

    reg_summary = RegionalAnalytics.get_regional_summary(filtered_df)
    store_summary = RegionalAnalytics.get_store_performance_summary(filtered_df)

    if not store_summary.empty:
        # Top 4 Micro-KPI Cards for Store Performance
        top_rev_store = store_summary.loc[store_summary["Revenue"].idxmax()]
        top_prof_store = store_summary.loc[store_summary["Profit_Margin_%"].idxmax()]
        top_orders_store = store_summary.loc[store_summary["Orders"].idxmax()]
        total_stores = len(store_summary)
        total_states = store_summary["State"].nunique() if "State" in store_summary.columns else 0

        kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
        with kpi_c1:
            st.markdown(f"""
                <div class="kpi-card kpi-blue">
                    <div class="kpi-title">🏆 Top Revenue Store</div>
                    <div style="font-size: 16px; font-weight: 700; color: #1E3A8A; margin: 2px 0;">{top_rev_store['Store Name']}</div>
                    <div style="font-size: 13px; color: #059669; font-weight: 700;">{format_currency(top_rev_store['Revenue'])}</div>
                    <div style="font-size: 11px; color: #64748B;">📍 {top_rev_store['City']}, {top_rev_store['State']}</div>
                </div>
            """, unsafe_allow_html=True)

        with kpi_c2:
            st.markdown(f"""
                <div class="kpi-card kpi-green">
                    <div class="kpi-title">💎 Highest Margin Store</div>
                    <div style="font-size: 16px; font-weight: 700; color: #059669; margin: 2px 0;">{top_prof_store['Store Name']}</div>
                    <div style="font-size: 13px; color: #2563EB; font-weight: 700;">{top_prof_store['Profit_Margin_%']:.2f}% Margin</div>
                    <div style="font-size: 11px; color: #64748B;">📍 {top_prof_store['City']} (Profit: {format_currency(top_prof_store['Profit'])})</div>
                </div>
            """, unsafe_allow_html=True)

        with kpi_c3:
            st.markdown(f"""
                <div class="kpi-card kpi-purple">
                    <div class="kpi-title">📦 Top Order Volume Store</div>
                    <div style="font-size: 16px; font-weight: 700; color: #7C3AED; margin: 2px 0;">{top_orders_store['Store Name']}</div>
                    <div style="font-size: 13px; color: #7C3AED; font-weight: 700;">{int(top_orders_store['Orders']):,} Orders</div>
                    <div style="font-size: 11px; color: #64748B;">📍 {top_orders_store['City']} (Units: {int(top_orders_store['Units_Sold']):,})</div>
                </div>
            """, unsafe_allow_html=True)

        with kpi_c4:
            st.markdown(f"""
                <div class="kpi-card kpi-teal">
                    <div class="kpi-title">🏬 Nationwide Retail Network</div>
                    <div style="font-size: 20px; font-weight: 800; color: #0D9488; margin: 2px 0;">{total_stores} Active Stores</div>
                    <div style="font-size: 13px; color: #0D9488; font-weight: 600;">Across {total_states} Indian States</div>
                    <div style="font-size: 11px; color: #64748B;">Coverage: South, West, North, East, Central</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Regional Pills Grid
        if not reg_summary.empty:
            r_cols = st.columns(len(reg_summary))
            for idx, (_, r_data) in enumerate(reg_summary.iterrows()):
                with r_cols[idx]:
                    reg_name = r_data["Region"]
                    reg_rev = r_data["Revenue"]
                    reg_share = r_data["Revenue_Share_%"]
                    reg_margin = r_data["Profit_Margin_%"]
                    store_count = len(store_summary[store_summary["Region"] == reg_name]) if "Region" in store_summary.columns else 0
                    
                    st.markdown(f"""
                        <div class="region-pill">
                            <h4>📍 {reg_name} Region</h4>
                            <div style="font-size: 17px; font-weight: 800; color: #1E3A8A; margin: 3px 0;">{format_currency(reg_rev)}</div>
                            <p>Share: <b>{reg_share:.1f}%</b> | Margin: <b>{reg_margin:.1f}%</b></p>
                            <p style="font-size: 11px; color: #64748B; margin-top: 2px;">🏬 <b>{store_count}</b> Active Retail Stores</p>
                        </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")

        # Interactive Map Control Toolbar
        st.markdown("#### 🎛️ Map GIS Controls & Styling")
        mc1, mc2, mc3, mc4 = st.columns(4)
        
        with mc1:
            map_theme_choice = st.selectbox(
                "Basemap Theme",
                [
                    "🏢 Enterprise Clean (Carto Positron)", 
                    "🌌 Executive Dark (Carto Dark Matter)", 
                    "🗺️ Streets & Topography (OpenStreetMap)", 
                    "🌐 High-Contrast Vector (Offline)"
                ],
                index=0
            )
            theme_map = {
                "🏢 Enterprise Clean (Carto Positron)": "carto-positron",
                "🌌 Executive Dark (Carto Dark Matter)": "carto-darkmatter",
                "🗺️ Streets & Topography (OpenStreetMap)": "open-street-map",
                "🌐 High-Contrast Vector (Offline)": "vector"
            }
            selected_theme = theme_map[map_theme_choice]

        with mc2:
            color_choice = st.selectbox(
                "Color Pins By",
                ["Profit Margin (%)", "Region (Zonal Breakdown)", "Store Format (Store Type)"],
                index=0
            )
            color_mode = "Profit Margin" if "Margin" in color_choice else ("Region" if "Region" in color_choice else "Store Type")

        with mc3:
            size_choice = st.selectbox(
                "Bubble Size Reflects",
                ["Sales Revenue (₹)", "Order Volume (Count)"],
                index=0
            )
            size_mode = "Revenue" if "Revenue" in size_choice else "Orders"

        with mc4:
            zoom_preset = st.selectbox(
                "Regional Focus / Zoom",
                [
                    "🇮🇳 All India (National Overview)",
                    "📍 South Region (Warangal, Hyderabad, BLR...)",
                    "📍 West Region (Mumbai, Pune, Ahmedabad)",
                    "📍 North Region (Delhi, Jaipur, Lucknow...)",
                    "📍 East & Central (Kolkata, Bhopal)"
                ],
                index=0
            )
            preset_coords = {
                "🇮🇳 All India (National Overview)": (21.8, 79.5, 4.3),
                "📍 South Region (Warangal, Hyderabad, BLR...)": (14.5, 78.5, 5.4),
                "📍 West Region (Mumbai, Pune, Ahmedabad)": (20.0, 73.5, 5.8),
                "📍 North Region (Delhi, Jaipur, Lucknow...)": (28.0, 77.5, 5.6),
                "📍 East & Central (Kolkata, Bhopal)": (23.0, 83.0, 5.4)
            }
            c_lat, c_lon, c_zoom = preset_coords[zoom_preset]

        # Map Coverage Perspective Switcher
        map_perspective = st.radio(
            "Select Map Coverage",
            ["🇮🇳 High-Definition India Retail Network", "🌍 Global Multi-Region View"],
            horizontal=True
        )

        if "India" in map_perspective:
            fig_map = ChartVisualizer.india_store_map(
                store_summary,
                title=f"🇮🇳 India Retail Network ({map_theme_choice.split('(')[0].strip()}) — Size: {size_choice} | Color: {color_choice}",
                map_style=selected_theme,
                color_by=color_mode,
                size_by=size_mode,
                center_lat=c_lat,
                center_lon=c_lon,
                zoom=c_zoom,
                height=720
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            fig_world = ChartVisualizer.world_store_map(
                store_summary,
                title="🌍 Global Multi-Region Geographic Sales Distribution",
                height=620
            )
            st.plotly_chart(fig_world, use_container_width=True)

        st.markdown("---")

        # Coordinated Charts Below Map
        col_m_chart1, col_m_chart2 = st.columns([7, 5])
        with col_m_chart1:
            top_stores_df = store_summary.head(8).sort_values("Revenue", ascending=True)
            fig_top_stores = px.bar(
                top_stores_df,
                x="Revenue",
                y="Store Name",
                orientation="h",
                color="Region",
                color_discrete_map=REGION_COLORS,
                title="<b>Top 8 Retail Stores by Gross Revenue (₹)</b>",
                template="plotly_white",
                text_auto=".2s"
            )
            fig_top_stores.update_layout(height=430, margin=dict(l=40, r=20, t=60, b=40))
            st.plotly_chart(fig_top_stores, use_container_width=True)

        with col_m_chart2:
            fig_reg_donut = ChartVisualizer.pie_chart(
                reg_summary,
                names="Region",
                values="Revenue",
                title="Regional Revenue Contribution Share",
                hole=0.55,
                height=430
            )
            st.plotly_chart(fig_reg_donut, use_container_width=True)

        st.markdown("---")

        # Store Leaderboard Table
        st.markdown("### 🏬 Complete Retail Store Performance Directory")
        st.caption("Granular directory of physical retail stores with revenue, gross profit, orders, units sold, and average order value.")
        
        display_cols = [
            "Store_Rank", "Store Name", "City", "State", "Region", "Store Type",
            "Revenue", "Profit", "Profit_Margin_%", "Orders", "Units_Sold", "Avg_Order_Value"
        ]
        valid_cols = [c for c in display_cols if c in store_summary.columns]
        
        st.dataframe(store_summary[valid_cols].style.format({
            "Revenue": "₹{:,.2f}", 
            "Profit": "₹{:,.2f}", 
            "Avg_Order_Value": "₹{:,.2f}",
            "Profit_Margin_%": "{:.2f}%",
            "Orders": "{:,}",
            "Units_Sold": "{:,}"
        }), use_container_width=True)

        # Download Store Sales Report
        col_rep1, col_rep2 = st.columns(2)
        with col_rep1:
            st.download_button(
                "⬇️ Export Store Performance Report (Excel .xlsx)",
                data=ExcelReportExporter.generate_excel_report(filtered_df),
                file_name="India_Multi_Store_Sales_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col_rep2:
            st.download_button(
                "⬇️ Export Regional Performance Summary (PDF)",
                data=PDFReportExporter.generate_pdf_report(filtered_df),
                file_name="India_Regional_Sales_Summary.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.warning("No store location data found in current selection.")


# ==============================================================================
# TAB 2: EXECUTIVE BI DASHBOARD
# ==============================================================================
with tab_dash:
    st.subheader("📊 Executive Business Intelligence Dashboard")

    if filtered_df.empty:
        st.warning("No data available in current filter selection.")
    else:
        kpis = ExecutiveAnalytics.compute_kpis(filtered_df)

        # 8 KPI Metric Cards with Proper Spacing
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(render_kpi_card("Total Revenue", format_currency(kpis["total_revenue"]), delta=f"{kpis['revenue_growth']:+.1f}% vs prior" if kpis['revenue_growth'] != 0 else None, delta_type="positive" if kpis["revenue_growth"] >= 0 else "negative", color_accent="blue"), unsafe_allow_html=True)
        c2.markdown(render_kpi_card("Total Profit", format_currency(kpis["total_profit"]), delta=f"{kpis['profit_growth']:+.1f}% vs prior" if kpis['profit_growth'] != 0 else None, delta_type="positive" if kpis["profit_growth"] >= 0 else "negative", color_accent="green"), unsafe_allow_html=True)
        c3.markdown(render_kpi_card("Total Orders", format_number(kpis["total_orders"]), color_accent="purple"), unsafe_allow_html=True)
        c4.markdown(render_kpi_card("Total Customers", format_number(kpis["total_customers"]), color_accent="amber"), unsafe_allow_html=True)

        c5, c6, c7, c8 = st.columns(4)
        c5.markdown(render_kpi_card("Products Sold (Units)", format_number(kpis["products_sold"]), color_accent="teal"), unsafe_allow_html=True)
        c6.markdown(render_kpi_card("Avg Order Value (AOV)", format_currency(kpis["avg_order_value"]), color_accent="blue"), unsafe_allow_html=True)
        c7.markdown(render_kpi_card("Profit Margin", f"{kpis['profit_margin']:.1f}%", color_accent="green"), unsafe_allow_html=True)
        c8.markdown(render_kpi_card("Revenue Growth Rate", f"{kpis['revenue_growth']:+.1f}%", delta_type="positive" if kpis["revenue_growth"] >= 0 else "negative", color_accent="rose"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Main Charts with Proper Margin and Zero Title Collisions
        col_d1, col_d2 = st.columns([7, 5])
        with col_d1:
            daily_df = SalesAnalytics.get_daily_sales(filtered_df)
            if not daily_df.empty:
                fig_daily = ChartVisualizer.line_chart(
                    daily_df, x="Order Date", y=["Revenue", "Rolling_7D_Revenue"], 
                    title="Daily Sales Trajectory with 7-Day Rolling Moving Average",
                    height=480
                )
                st.plotly_chart(fig_daily, use_container_width=True)

        with col_d2:
            cat_df = ProductAnalytics.get_category_breakdown(filtered_df)
            if not cat_df.empty:
                fig_cat = ChartVisualizer.bar_chart(
                    cat_df, x="Category", y="Revenue", 
                    title="Category-wise Revenue Contribution (₹)", 
                    color="Category",
                    height=480
                )
                st.plotly_chart(fig_cat, use_container_width=True)

        col_d3, col_d4 = st.columns(2)
        with col_d3:
            if "Payment Method" in filtered_df.columns:
                pm_df = filtered_df.groupby("Payment Method")["Revenue"].sum().reset_index()
                fig_pm = ChartVisualizer.pie_chart(
                    pm_df, names="Payment Method", values="Revenue", 
                    title="Revenue Share by Payment Channel", 
                    hole=0.54,
                    height=460
                )
                st.plotly_chart(fig_pm, use_container_width=True)
        with col_d4:
            reg_df = RegionalAnalytics.get_regional_summary(filtered_df)
            if not reg_df.empty:
                fig_reg = ChartVisualizer.pie_chart(
                    reg_df, names="Region", values="Revenue", 
                    title="Regional Revenue Contribution Share", 
                    hole=0.54,
                    height=460
                )
                st.plotly_chart(fig_reg, use_container_width=True)


# ==============================================================================
# TAB 3: DATA CLEANING LAB
# ==============================================================================
with tab_clean:
    st.subheader("🧹 Interactive Data Cleaning Lab")
    st.caption("Inspect raw datasets, discover missing values across columns, choose custom imputation strategies, review exact cell-level changes, and examine statistical impacts.")

    if df_raw is None:
        st.info("👆 Please upload a CSV file or click 'Load Raw Dataset' in the sidebar to start data cleaning.")
    else:
        st.markdown(f"**Inspecting Dataset:** `{fname}.csv` &nbsp;|&nbsp; **Shape:** `{df_raw.shape[0]:,} rows` × `{df_raw.shape[1]} columns`")

        # Step 1: Missing and Duplicate Value Audit
        st.markdown("### Step 1 — Find Missing & Duplicate Records")
        
        # Check Duplicates
        dup_col = ["Order ID"] if "Order ID" in df_raw.columns else None
        dup_count = int(df_raw.duplicated(subset=dup_col).sum())
        
        if dup_count > 0:
            st.warning(f"⚠️ **Duplicate Records Detected:** Found **{dup_count} duplicate transaction rows** (Identical Order IDs generated by POS double-swiping or network retries). Deduplication will remove them to prevent revenue inflation.")
            remove_dups_choice = st.checkbox(f"✅ Delete {dup_count} duplicate transaction rows during cleaning (Recommended)", value=True)
        else:
            st.success("✓ No duplicate rows detected in this dataset.")
            remove_dups_choice = True

        miss = pd.DataFrame({
            "Column Name": df_raw.columns,
            "Data Type": [str(t) for t in df_raw.dtypes],
            "Missing Count": df_raw.isna().sum().values,
            "Missing Percentage (%)": (df_raw.isna().mean() * 100).round(2).values,
        })
        miss_cols = miss[miss["Missing Count"] > 0]
        
        col_m1, col_m2 = st.columns([1, 1.3])
        with col_m1:
            st.dataframe(miss, hide_index=True, use_container_width=True)
        with col_m2:
            if miss_cols.empty:
                st.success("🎉 No missing values detected in this file! All columns are 100% complete.")
            else:
                sample_n = min(150, len(df_raw))
                sample = df_raw.head(sample_n)
                fig, ax = plt.subplots(figsize=(7, 3.8))
                sns.heatmap(sample.isna(), cbar=False, cmap=["#E2E8F0", "#EF4444"], yticklabels=False, ax=ax)
                ax.set_title(f"Missing-Value Map (Red = Missing, First {sample_n} Rows)", fontsize=10, fontweight="bold")
                st.pyplot(fig)

        if not miss_cols.empty or dup_count > 0:
            # Step 2: Choose strategy
            st.markdown("### Step 2 — Choose How to Fill Each Column")
            st.caption("Smart defaults: Numeric $\\to$ `median`, Categorical $\\to$ `mode`. Date columns are left as-is. Adjust any column below:")

            strategies, constants = {}, {}
            grid = st.columns(3)
            for n, col in enumerate(miss_cols["Column Name"]):
                numeric = pd.api.types.is_numeric_dtype(df_raw[col])
                opts = (["median", "mean", "mode", "zero", "constant", "drop rows", "leave as is"] if numeric
                        else ["mode", "constant", "drop rows", "leave as is"])
                with grid[n % 3]:
                    strategies[col] = st.selectbox(
                        f"**{col}** ({int(miss_cols.set_index('Column Name').at[col, 'Missing Count'])} missing)",
                        opts, index=opts.index(default_strategy(df_raw, col)), key=f"s_{fname}_{col}"
                    )
                    if strategies[col] == "constant":
                        constants[col] = st.text_input(
                            f"Constant value for {col}", value="0" if numeric else "Unknown",
                            key=f"c_{fname}_{col}"
                        )

            cleaned, log_df = clean_dataframe(df_raw, strategies, constants, remove_duplicates=remove_dups_choice)

            # Step 3: What changed?
            st.markdown("### Step 3 — What Changed?")
            total_missing = int(df_raw.isna().sum().sum())
            remaining = int(cleaned.isna().sum().sum())
            dups_dropped = len([x for x in log_df.to_dict('records') if x.get('method') == 'drop duplicate row']) if not log_df.empty else 0
            total_rows_dropped = len(df_raw) - len(cleaned)

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Missing Cells (Before)", f"{total_missing:,}")
            k2.metric("Duplicate Rows Deleted", f"{dups_dropped:,} rows")
            k3.metric("Total Rows Dropped", f"{total_rows_dropped:,} rows")
            k4.metric("Clean Records Active", f"{len(cleaned):,} rows")

            st.markdown("""
                <div class="insight-box" style="margin: 14px 0;">
                    <b>🎓 Data Science Rationale (For Professor / Project Evaluation):</b><br>
                    <b>1. Why delete duplicate rows?</b><br>
                    Duplicate records occur when retail Point-of-Sale (POS) card terminals retry failed connections or double-swipe. Keeping them falsely multiplies revenue, customer counts, and profit. Therefore, deleting duplicate records is essential for accounting accuracy.<br><br>
                    <b>2. Why impute missing values instead of deleting entire rows?</b><br>
                    Deleting an entire transaction row (called <i>listwise deletion</i>) simply because a non-critical field like <code>Customer Segment</code> or <code>Discount</code> is blank would discard authentic product sales of ₹50,000 to ₹1,00,000! 
                    Doing so artificially shrinks total enterprise revenue. Instead, modern business intelligence uses <b>Statistical Imputation</b> (median for numeric, mode for categorical), which preserves valid financial transactions while restoring data completeness.
                </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 📜 Cleaning Log — Exact Row and Column of Every Modification")
            if log_df.empty:
                st.info("All selected strategies are 'leave as is' — no cells were modified.")
            else:
                st.dataframe(log_df.head(250), hide_index=True, use_container_width=True)
                summ = (log_df.groupby(["column", "method", "new_value"]).size().reset_index(name="cells_changed"))
                st.markdown("**Summary of Changes by Column**")
                st.dataframe(summ, hide_index=True, use_container_width=True)

            v1, v2 = st.tabs(["🔴 Before (Missing = Red)", "🟢 After (Filled = Green)"])
            only_missing = st.checkbox("Show only rows that had a missing value", value=True)
            rows = df_raw.index[df_raw.isna().any(axis=1)] if only_missing else df_raw.index
            rows = rows[:150]
            with v1:
                st.dataframe(highlight(df_raw.loc[rows], df_raw.loc[rows].isna(), "#FECACA"), use_container_width=True)
            with v2:
                keep = [r for r in rows if r in cleaned.index]
                filled_mask = df_raw.isna().loc[keep] & cleaned.loc[keep].notna()
                st.dataframe(highlight(cleaned.loc[keep], filled_mask, "#BBF7D0"), use_container_width=True)

            # Step 4: Impact on the statistics
            num_cols = [c for c in miss_cols["Column Name"] if pd.api.types.is_numeric_dtype(df_raw[c])]
            if num_cols:
                st.markdown("### Step 4 — Impact on Statistics")
                stats = pd.DataFrame({
                    "Mean (Before)": df_raw[num_cols].mean(),
                    "Mean (After)": cleaned[num_cols].mean(),
                    "Median (Before)": df_raw[num_cols].median(),
                    "Median (After)": cleaned[num_cols].median(),
                    "Std Dev (Before)": df_raw[num_cols].std(),
                    "Std Dev (After)": cleaned[num_cols].std(),
                }).round(3)
                st.dataframe(stats, use_container_width=True)

                pick = st.selectbox("Select numeric feature to inspect distribution (Before vs After)", num_cols)
                fig, ax = plt.subplots(figsize=(8, 3.2))
                sns.histplot(df_raw[pick].dropna(), color="#3B82F6", label="Before Cleaning", alpha=0.55, bins=25, ax=ax)
                sns.histplot(cleaned[pick].dropna(), color="#10B981", label="After Cleaning & Imputation", alpha=0.45, bins=25, ax=ax)
                ax.set_title(f"Distribution Comparison for {pick}: Before vs After", fontsize=11, fontweight="bold")
                ax.legend()
                st.pyplot(fig)

            # Step 5: Save & Push to Analytics
            st.markdown("### Step 5 — Save Clean Data + Log")
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                if st.button("💾 Save Clean File and Log to ./data", type="primary", use_container_width=True):
                    cp = os.path.join(DATA_DIR, f"clean_{fname.replace('raw_', '')}.csv")
                    lp = os.path.join(DATA_DIR, f"cleaning_log_{fname.replace('raw_', '')}.csv")
                    cleaned.to_csv(cp, index=False)
                    log_df.to_csv(lp, index=False)
                    st.success(f"✓ Saved cleaned dataset to `{cp}` and audit log to `{lp}`")
            with col_s2:
                if st.button("🚀 Push to Active Analytics Dashboard", use_container_width=True):
                    st.session_state.active_cleaned_df = cleaned
                    st.session_state.active_dataset_name = f"clean_{fname}.csv"
                    db_manager.save_sales_records(cleaned)
                    st.success("✓ Dataset is now active across all dashboard tabs!")
            with col_s3:
                st.download_button(
                    "⬇️ Download Cleaned CSV",
                    data=cleaned.to_csv(index=False).encode(),
                    file_name=f"clean_{fname}.csv",
                    mime="text/csv",
                    use_container_width=True
                )


# ==============================================================================
# TAB 4: REGIONAL COMPARISONS
# ==============================================================================
with tab_cmp:
    st.subheader("⚖️ Regional & Multi-Store Comparative Analytics")
    st.caption("Side-by-side performance comparison between Indian geographic regions, store formats, or product categories.")

    active_df = st.session_state.active_cleaned_df
    cmp_dimension = st.radio("Select Comparison Level", ["Region", "Store Type", "Category"], horizontal=True)

    if cmp_dimension in active_df.columns:
        unique_vals = sorted(list(active_df[cmp_dimension].dropna().unique()))
        selected_entities = st.multiselect(f"Select 2 to 3 {cmp_dimension}s to compare", unique_vals, default=unique_vals[:min(3, len(unique_vals))])

        if len(selected_entities) < 2:
            st.warning("Please select at least 2 entities to display a side-by-side comparison.")
        else:
            cmp_df = active_df[active_df[cmp_dimension].isin(selected_entities)]

            scorecard = cmp_df.groupby(cmp_dimension).agg(
                Revenue=("Revenue", "sum"),
                Profit=("Profit", "sum"),
                Orders=("Order ID", "nunique"),
                Units=("Quantity", "sum")
            ).reset_index()
            scorecard["Profit Margin %"] = ((scorecard["Profit"] / scorecard["Revenue"]) * 100).round(2)
            scorecard["AOV"] = (scorecard["Revenue"] / scorecard["Orders"]).round(2)

            st.markdown("#### 🏆 Comparative Scorecard")
            sc_cols = st.columns(len(selected_entities))
            for idx, (_, row) in enumerate(scorecard.iterrows()):
                with sc_cols[idx]:
                    st.markdown(f"### {row[cmp_dimension]}")
                    st.metric("Total Sales", format_currency(row["Revenue"]))
                    st.metric("Profit Margin", f"{row['Profit Margin %']:.1f}%")
                    st.caption(f"{int(row['Orders']):,} orders | {int(row['Units']):,} units sold | AOV: ₹{row['AOV']:,.2f}")

            st.divider()

            c_cmp1, c_cmp2 = st.columns(2)
            with c_cmp1:
                st.markdown("**Sales vs Gross Profit Comparison**")
                m_score = scorecard.melt(id_vars=cmp_dimension, value_vars=["Revenue", "Profit"], var_name="Metric", value_name="Value")
                fig_sc = px.bar(m_score, x=cmp_dimension, y="Value", color="Metric", barmode="group", template="plotly_white")
                fig_sc.update_layout(height=420, margin=dict(t=50, b=40))
                st.plotly_chart(fig_sc, use_container_width=True)

            with c_cmp2:
                st.markdown("**Relative Performance Radar Profile**")
                cats = ["Revenue", "Profit", "Orders", "AOV"]
                fig_radar = go.Figure()
                for _, r in scorecard.iterrows():
                    norm_vals = [
                        (r["Revenue"] / scorecard["Revenue"].max()) * 100,
                        (r["Profit"] / scorecard["Profit"].max()) * 100,
                        (r["Orders"] / scorecard["Orders"].max()) * 100,
                        (r["AOV"] / scorecard["AOV"].max()) * 100,
                    ]
                    fig_radar.add_trace(go.Scatterpolar(
                        r=norm_vals + norm_vals[:1],
                        theta=cats + cats[:1],
                        fill="toself",
                        name=str(r[cmp_dimension]),
                        opacity=0.55
                    ))
                fig_radar.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), height=420, margin=dict(l=40, r=40, t=30, b=30))
                st.plotly_chart(fig_radar, use_container_width=True)


# ==============================================================================
# TAB 5: MACHINE LEARNING LAB
# ==============================================================================
with tab_ml:
    st.subheader("🤖 Machine Learning & Predictive Analytics")
    active_df = st.session_state.active_cleaned_df

    ml_sub1, ml_sub2, ml_sub3 = st.tabs([
        "🔮 Future Sales Forecasting",
        "📦 Demand Prediction (Random Forest)",
        "👥 Customer RFM Clustering"
    ])

    with ml_sub1:
        st.markdown("#### 🔮 Sales Forecasting (Ridge Regression + Seasonal Lags)")
        days_ahead = st.slider("Select Forecast Horizon (Days)", 15, 90, 45, step=15)
        forecast_df, f_metrics = SalesForecaster.forecast_sales(active_df, days_ahead=days_ahead)
        
        if not forecast_df.empty:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("MAE", format_currency(f_metrics.get("MAE", 0)))
            m2.metric("RMSE", format_currency(f_metrics.get("RMSE", 0)))
            m3.metric("MAPE (%)", f"{f_metrics.get('MAPE_%', 0):.1f}%")
            m4.metric("Model R² Score", f"{f_metrics.get('R2_Score', 0):.3f}")

            st.plotly_chart(ChartVisualizer.forecast_chart(forecast_df, title=f"Next {days_ahead} Days Sales Forecast"), use_container_width=True)

    with ml_sub2:
        st.markdown("#### 📦 Product Demand Regressor & What-If Simulator")
        dp = DemandPredictor()
        dp_metrics = dp.train(active_df)

        if dp_metrics:
            d1, d2, d3 = st.columns(3)
            d1.metric("Model MAE", f"{dp_metrics['MAE']} units")
            d2.metric("Model RMSE", f"{dp_metrics['RMSE']} units")
            d3.metric("Model R²", f"{dp_metrics['R2_Score']:.3f}")

            st.markdown("##### 🧪 Interactive What-If Demand Simulator")
            w1, w2, w3, w4, w5 = st.columns(5)
            with w1: sim_cat = st.selectbox("Category", dp.category_list if dp.category_list else ["Electronics"])
            with w2: sim_reg = st.selectbox("Region", dp.region_list if dp.region_list else ["South"])
            with w3: sim_seg = st.selectbox("Segment", dp.segment_list if dp.segment_list else ["Consumer"])
            with w4: sim_price = st.number_input("Unit Price (₹)", min_value=100.0, max_value=200000.0, value=25000.0, step=1000.0)
            with w5: sim_disc = st.slider("Discount (%)", 0, 30, 10, step=5) / 100.0

            res = dp.predict_scenario(sim_price, sim_disc, sim_cat, sim_reg, sim_seg)
            st.success(f"🎯 **Predicted Order Demand:** `{res['predicted_quantity']} units` &nbsp;|&nbsp; 💵 **Projected Revenue:** `{format_currency(res['predicted_revenue'])}`")

    with ml_sub3:
        st.markdown("#### 👥 Unsupervised K-Means Customer Clustering (RFM + PCA)")
        k_val = st.slider("Number of Clusters (K)", 2, 6, 4)
        rfm_base = CustomerAnalytics.calculate_rfm(active_df)
        clustered_df, c_metrics = CustomerClusterer.cluster_customers(rfm_base, n_clusters=k_val)

        if not clustered_df.empty:
            km1, km2 = st.columns(2)
            km1.metric("Silhouette Score", f"{c_metrics['silhouette_score']:.3f}")
            km2.metric("Inertia", f"{c_metrics['inertia']:.1f}")

            st.plotly_chart(ChartVisualizer.scatter_plot(clustered_df, x="PCA1", y="PCA2", color="Cluster_Persona", hover_name="Customer Name", title="2D PCA Customer Clusters"), use_container_width=True)
            st.dataframe(c_metrics["cluster_profiles"].style.format({
                "Recency_Mean": "{:.1f} days", "Frequency_Mean": "{:.1f} orders", "Monetary_Mean": "₹{:,.2f}"
            }), use_container_width=True)


# ==============================================================================
# TAB 6: RAW & CLEAN DATA FILES
# ==============================================================================
with tab_raw_files:
    st.subheader("📁 Raw & Cleaned Data Files in `./data`")
    st.caption("All saved raw and clean CSV files stored in the project's `./data` directory:")

    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.csv")))
    if not files:
        st.info("No CSV files located in `./data/`.")
    else:
        for fpath in files:
            bname = os.path.basename(fpath)
            f_df = pd.read_csv(fpath)
            with st.expander(f"📄 {bname} ({len(f_df):,} rows × {f_df.shape[1]} cols)"):
                st.dataframe(f_df.head(50), use_container_width=True)
                st.download_button(
                    f"Download {bname}",
                    data=f_df.to_csv(index=False).encode(),
                    file_name=bname,
                    mime="text/csv",
                    key=f"dl_file_{bname}"
                )


# ==============================================================================
# TAB 7: REPORTS & STRATEGIC INSIGHTS
# ==============================================================================
with tab_reports:
    st.subheader("📑 Executive Reports & Strategic Insights")
    active_df = st.session_state.active_cleaned_df

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        pdf_bytes = PDFReportExporter.generate_pdf_report(active_df)
        st.download_button("📄 Download Executive PDF Report", data=pdf_bytes, file_name="Smart_Retail_Report.pdf", mime="application/pdf", use_container_width=True)
    with r_col2:
        excel_bytes = ExcelReportExporter.generate_excel_report(active_df)
        st.download_button("📊 Download Multi-Tab Excel Workbook (.xlsx)", data=excel_bytes, file_name="Smart_Retail_Workbook.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    st.markdown("---")
    st.markdown("#### 💡 Automated Business Insights")
    insights = InsightsGenerator.generate_insights(active_df)
    for item in insights:
        box_class = "insight-box" if item["type"] == "positive" else ("warning-box" if item["type"] == "warning" else "insight-box")
        st.markdown(f"""
            <div class="{box_class}">
                <b>[{item['category']}] {item['title']}</b><br>
                {item['detail']}
            </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# TAB 8: ACADEMIC REPORT (SR UNIVERSITY)
# ==============================================================================
with tab_academic:
    st.subheader("🎓 SR University Academic Project Report")
    st.info("Formatted strictly per SR University Data Analytics and Visualization (25CAI202PC201) curriculum requirements.")

    doc_path = os.path.join(TEMPLATES_DIR, "academic_project_report.docx")
    md_path = os.path.join(TEMPLATES_DIR, "academic_project_report.md")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        if os.path.exists(doc_path):
            with open(doc_path, "rb") as f:
                st.download_button("📥 Download Official Word Report (.docx)", data=f.read(), file_name="Smart_Retail_SR_University_Report.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
    with col_d2:
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8") as f:
                st.download_button("📄 Download Markdown Report (.md)", data=f.read(), file_name="Smart_Retail_Report.md", mime="text/markdown", use_container_width=True)

    st.markdown("---")
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            st.markdown(f.read())

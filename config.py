"""
Smart Retail Sales Analytics & Visualization System
Configuration & Application Settings
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
ASSETS_DIR = BASE_DIR / "assets"
REPORTS_DIR = BASE_DIR / "reports"
TEMPLATES_DIR = BASE_DIR / "templates"

# Database Configuration
DATABASE_PATH = DATABASE_DIR / "retail_analytics.db"

# Sample Data Files
SAMPLE_CSV_PATH = DATA_DIR / "retail_sales_sample.csv"
SAMPLE_EXCEL_PATH = DATA_DIR / "retail_sales_sample.xlsx"

# App Branding
APP_TITLE = "Smart Retail Sales Analytics & Multi-Store BI System"
APP_SUBTITLE = "Enterprise Multi-Region Retail Operations, Data Cleaning & Predictive Intelligence"
COURSE_NAME = "Data Analytics and Visualization (25CAI202PC201)"
INSTITUTION = "SR UNIVERSITY - School of Computer Science & Artificial Intelligence"
ACADEMIC_YEAR = "2026-27"

# Theme Palettes
COLOR_PALETTE = {
    "primary": "#1E3A8A",      # Deep Navy
    "secondary": "#2563EB",    # Royal Blue
    "accent": "#0D9488",       # Teal
    "success": "#10B981",      # Emerald Green
    "warning": "#F59E0B",      # Amber
    "danger": "#EF4444",       # Crimson Red
    "info": "#6366F1",         # Indigo
    "dark_bg": "#0F172A",      # Slate 900
    "card_bg": "#FFFFFF",      # Pure White
    "card_dark": "#1E293B",    # Slate 800
    "text_dark": "#0F172A",
    "text_light": "#F8FAFC",
    "neutral_gray": "#64748B"
}

# Chart Color Sequences
CHART_COLORS = [
    "#1E3A8A", "#2563EB", "#0D9488", "#10B981", 
    "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", 
    "#14B8A6", "#F97316", "#06B6D4", "#84CC16"
]

# Regional and Store Type Color Mappings
REGION_COLORS = {
    "South": "#2563EB",    # Royal Blue
    "West": "#F59E0B",     # Amber
    "North": "#10B981",    # Emerald
    "East": "#8B5CF6",     # Violet
    "Central": "#0D9488"   # Teal
}

STORE_TYPE_COLORS = {
    "Flagship": "#1E3A8A",
    "Superstore": "#2563EB",
    "Hypermarket": "#0D9488",
    "Express Mart": "#10B981",
    "Mall Outlet": "#F59E0B"
}

# Standard Column Schema for Smart Retail Multi-Store System
EXPECTED_COLUMNS = [
    "Order ID", "Order Date", "Store ID", "Store Name", "Store Type",
    "Customer ID", "Customer Name", "Customer Segment", 
    "Country", "State", "City", "Region", "Latitude", "Longitude",
    "Product ID", "Product Name", "Category", "Sub-Category", 
    "Quantity", "Unit Price", "Unit Cost", "Discount", 
    "Revenue", "Cost", "Profit", "Profit Margin", 
    "Payment Method", "Order Priority"
]

# Accurate Geographic Coordinates for Indian Cities & Retail Stores
INDIAN_STORES_INFO = {
    "Warangal": {
        "store_id": "STR-WGL-01",
        "store_name": "Warangal Mega Mart - Naimnagar",
        "store_type": "Superstore",
        "state": "Telangana",
        "region": "South",
        "lat": 17.9784,
        "lon": 79.5941
    },
    "Hyderabad": {
        "store_id": "STR-HYD-01",
        "store_name": "Hyderabad Flagship - Banjara Hills",
        "store_type": "Flagship",
        "state": "Telangana",
        "region": "South",
        "lat": 17.3850,
        "lon": 78.4867
    },
    "Bengaluru": {
        "store_id": "STR-BLR-01",
        "store_name": "Bengaluru Tech Hub - Koramangala",
        "store_type": "Hypermarket",
        "state": "Karnataka",
        "region": "South",
        "lat": 12.9716,
        "lon": 77.5946
    },
    "Chennai": {
        "store_id": "STR-MAA-01",
        "store_name": "Chennai Coastal Mart - T Nagar",
        "store_type": "Superstore",
        "state": "Tamil Nadu",
        "region": "South",
        "lat": 13.0827,
        "lon": 80.2707
    },
    "Kochi": {
        "store_id": "STR-COK-01",
        "store_name": "Kochi Marine Retail - MG Road",
        "store_type": "Mall Outlet",
        "state": "Kerala",
        "region": "South",
        "lat": 9.9312,
        "lon": 76.2673
    },
    "Visakhapatnam": {
        "store_id": "STR-VTZ-01",
        "store_name": "Vizag Harbor Outlet - Beach Road",
        "store_type": "Superstore",
        "state": "Andhra Pradesh",
        "region": "South",
        "lat": 17.6868,
        "lon": 83.2185
    },
    "Vijayawada": {
        "store_id": "STR-VJA-01",
        "store_name": "Vijayawada Center - Benz Circle",
        "store_type": "Express Mart",
        "state": "Andhra Pradesh",
        "region": "South",
        "lat": 16.5062,
        "lon": 80.6480
    },
    "Mumbai": {
        "store_id": "STR-BOM-01",
        "store_name": "Mumbai Central Flagship - Lower Parel",
        "store_type": "Flagship",
        "state": "Maharashtra",
        "region": "West",
        "lat": 19.0760,
        "lon": 72.8777
    },
    "Pune": {
        "store_id": "STR-PNQ-01",
        "store_name": "Pune Retail Hub - Viman Nagar",
        "store_type": "Hypermarket",
        "state": "Maharashtra",
        "region": "West",
        "lat": 18.5204,
        "lon": 73.8567
    },
    "Ahmedabad": {
        "store_id": "STR-AMD-01",
        "store_name": "Ahmedabad Commerce Mart - SG Highway",
        "store_type": "Superstore",
        "state": "Gujarat",
        "region": "West",
        "lat": 23.0225,
        "lon": 72.5714
    },
    "Delhi": {
        "store_id": "STR-DEL-01",
        "store_name": "Delhi Metro Store - Connaught Place",
        "store_type": "Flagship",
        "state": "Delhi",
        "region": "North",
        "lat": 28.7041,
        "lon": 77.1025
    },
    "Jaipur": {
        "store_id": "STR-JAI-01",
        "store_name": "Jaipur Heritage Store - MI Road",
        "store_type": "Superstore",
        "state": "Rajasthan",
        "region": "North",
        "lat": 26.9124,
        "lon": 75.7873
    },
    "Lucknow": {
        "store_id": "STR-LKO-01",
        "store_name": "Lucknow Premier Mart - Hazratganj",
        "store_type": "Mall Outlet",
        "state": "Uttar Pradesh",
        "region": "North",
        "lat": 26.8467,
        "lon": 80.9462
    },
    "Chandigarh": {
        "store_id": "STR-IXC-01",
        "store_name": "Chandigarh Sector Store - Sector 17",
        "store_type": "Express Mart",
        "state": "Punjab",
        "region": "North",
        "lat": 30.7333,
        "lon": 76.7794
    },
    "Kolkata": {
        "store_id": "STR-CCU-01",
        "store_name": "Kolkata City Store - Park Street",
        "store_type": "Flagship",
        "state": "West Bengal",
        "region": "East",
        "lat": 22.5726,
        "lon": 88.3639
    },
    "Bhopal": {
        "store_id": "STR-BHO-01",
        "store_name": "Bhopal Central Mart - MP Nagar",
        "store_type": "Superstore",
        "state": "Madhya Pradesh",
        "region": "Central",
        "lat": 23.2599,
        "lon": 77.4126
    }
}

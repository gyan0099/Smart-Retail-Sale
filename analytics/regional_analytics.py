"""
Smart Retail Sales Analytics & Visualization System
Regional & Multi-Store Analytics Engine
Analyzes performance across geographic Regions, States, Cities, and physical Retail Shops.
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import INDIAN_STORES_INFO

class RegionalAnalytics:
    """Computes geographic sales distribution and multi-store retail benchmarks."""

    @staticmethod
    def get_regional_summary(df: pd.DataFrame) -> pd.DataFrame:
        """Aggregates performance by Region (North, South, East, West, Central)."""
        if "Region" not in df.columns or "Revenue" not in df.columns:
            return pd.DataFrame()

        reg_df = df.groupby("Region").agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Units_Sold=("Quantity", "sum")
        ).reset_index()

        total_rev = reg_df["Revenue"].sum()
        reg_df["Revenue_Share_%"] = ((reg_df["Revenue"] / total_rev) * 100).round(2) if total_rev > 0 else 0
        reg_df["Profit_Margin_%"] = ((reg_df["Profit"] / reg_df["Revenue"]) * 100).round(2)
        reg_df["Avg_Order_Value"] = (reg_df["Revenue"] / reg_df["Orders"]).round(2)
        return reg_df.sort_values(by="Revenue", ascending=False).reset_index(drop=True)

    @staticmethod
    def get_store_performance_summary(df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregates performance at the physical Retail Shop / Store level.
        Enriches with coordinates, store type, and profitability rankings.
        """
        if df.empty or "Revenue" not in df.columns:
            return pd.DataFrame()

        # Check if Store ID / Store Name exist, otherwise fallback to City
        store_col = "Store Name" if "Store Name" in df.columns else "City"
        group_cols = [c for c in [store_col, "Store ID", "Store Type", "City", "State", "Region", "Latitude", "Longitude"] if c in df.columns]

        store_df = df.groupby(group_cols).agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Units_Sold=("Quantity", "sum")
        ).reset_index()

        # If Latitude/Longitude were missing, populate from config
        if "Latitude" not in store_df.columns or store_df["Latitude"].isnull().all():
            store_df["Latitude"] = store_df["City"].map(lambda c: INDIAN_STORES_INFO.get(c, {}).get("lat", np.nan))
            store_df["Longitude"] = store_df["City"].map(lambda c: INDIAN_STORES_INFO.get(c, {}).get("lon", np.nan))
        if "Store Name" not in store_df.columns:
            store_df["Store Name"] = store_df["City"].map(lambda c: INDIAN_STORES_INFO.get(c, {}).get("store_name", f"{c} Retail Outlet"))

        store_df["Profit_Margin_%"] = ((store_df["Profit"] / store_df["Revenue"]) * 100).round(2)
        store_df["Profit Margin"] = store_df["Profit_Margin_%"]
        store_df["Avg_Order_Value"] = (store_df["Revenue"] / store_df["Orders"]).round(2)

        store_df = store_df.sort_values(by="Revenue", ascending=False).reset_index(drop=True)
        store_df["Store_Rank"] = range(1, len(store_df) + 1)
        return store_df

    @staticmethod
    def get_state_summary(df: pd.DataFrame) -> pd.DataFrame:
        """Aggregates performance by State."""
        if "State" not in df.columns or "Revenue" not in df.columns:
            return pd.DataFrame()

        state_df = df.groupby(["State", "Region"]).agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Units_Sold=("Quantity", "sum")
        ).reset_index()

        state_df["Profit_Margin_%"] = ((state_df["Profit"] / state_df["Revenue"]) * 100).round(2)
        return state_df.sort_values(by="Revenue", ascending=False).reset_index(drop=True)

    @staticmethod
    def get_city_summary(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
        """Aggregates performance by City."""
        if "City" not in df.columns or "Revenue" not in df.columns:
            return pd.DataFrame()

        city_df = df.groupby(["City", "State", "Region"]).agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Units_Sold=("Quantity", "sum")
        ).reset_index()

        city_df["Profit_Margin_%"] = ((city_df["Profit"] / city_df["Revenue"]) * 100).round(2)
        city_df["Latitude"] = city_df["City"].map(lambda c: INDIAN_STORES_INFO.get(c, {}).get("lat", np.nan))
        city_df["Longitude"] = city_df["City"].map(lambda c: INDIAN_STORES_INFO.get(c, {}).get("lon", np.nan))

        sorted_df = city_df.sort_values(by="Revenue", ascending=False).reset_index(drop=True)
        return sorted_df.head(top_n) if top_n > 0 else sorted_df

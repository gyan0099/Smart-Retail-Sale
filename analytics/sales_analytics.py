"""
Smart Retail Sales Analytics & Visualization System
Sales Analytics Engine
Analyzes daily, monthly, yearly sales trends, seasonality, and growth rates.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class SalesAnalytics:
    """Computes granular time-series and periodic sales performance metrics."""

    @staticmethod
    def get_daily_sales(df: pd.DataFrame) -> pd.DataFrame:
        """Computes daily revenue, orders, and 7-day rolling moving average."""
        if "Order Date" not in df.columns or "Revenue" not in df.columns:
            return pd.DataFrame()

        df_daily = df.copy()
        df_daily["Order Date"] = pd.to_datetime(df_daily["Order Date"])
        daily = df_daily.groupby("Order Date").agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Units=("Quantity", "sum")
        ).reset_index().sort_values("Order Date")

        daily["Rolling_7D_Revenue"] = daily["Revenue"].rolling(window=7, min_periods=1).mean().round(2)
        daily["Cumulative_Revenue"] = daily["Revenue"].cumsum().round(2)
        return daily

    @staticmethod
    def get_monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
        """Computes monthly aggregated sales, profit, orders, and Month-over-Month (MoM) growth."""
        if "Order Date" not in df.columns or "Revenue" not in df.columns:
            return pd.DataFrame()

        df_m = df.copy()
        df_m["Order Date"] = pd.to_datetime(df_m["Order Date"])
        df_m["Year_Month"] = df_m["Order Date"].dt.to_period("M").astype(str)

        monthly = df_m.groupby("Year_Month").agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Cost=("Cost", "sum"),
            Orders=("Order ID", "nunique"),
            Units=("Quantity", "sum")
        ).reset_index().sort_values("Year_Month")

        monthly["Profit_Margin_%"] = ((monthly["Profit"] / monthly["Revenue"]) * 100).round(2)
        monthly["MoM_Revenue_Growth_%"] = (monthly["Revenue"].pct_change() * 100).round(2).fillna(0.0)
        monthly["MoM_Profit_Growth_%"] = (monthly["Profit"].pct_change() * 100).round(2).fillna(0.0)
        return monthly

    @staticmethod
    def get_yearly_sales(df: pd.DataFrame) -> pd.DataFrame:
        """Computes yearly aggregated sales, profit, orders, and Year-over-Year (YoY) growth."""
        if "Order Date" not in df.columns or "Revenue" not in df.columns:
            return pd.DataFrame()

        df_y = df.copy()
        df_y["Order Date"] = pd.to_datetime(df_y["Order Date"])
        df_y["Year"] = df_y["Order Date"].dt.year.astype(str)

        yearly = df_y.groupby("Year").agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Units=("Quantity", "sum")
        ).reset_index().sort_values("Year")

        yearly["Profit_Margin_%"] = ((yearly["Profit"] / yearly["Revenue"]) * 100).round(2)
        yearly["YoY_Revenue_Growth_%"] = (yearly["Revenue"].pct_change() * 100).round(2).fillna(0.0)
        yearly["Avg_Order_Value"] = (yearly["Revenue"] / yearly["Orders"]).round(2)
        return yearly

    @staticmethod
    def get_day_of_week_sales(df: pd.DataFrame) -> pd.DataFrame:
        """Analyzes sales performance across days of the week."""
        if "Order Date" not in df.columns or "Revenue" not in df.columns:
            return pd.DataFrame()

        df_dow = df.copy()
        df_dow["Order Date"] = pd.to_datetime(df_dow["Order Date"])
        df_dow["Day_Name"] = df_dow["Order Date"].dt.day_name()
        df_dow["Day_Index"] = df_dow["Order Date"].dt.dayofweek

        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_stats = df_dow.groupby(["Day_Index", "Day_Name"]).agg(
            Total_Revenue=("Revenue", "sum"),
            Average_Revenue=("Revenue", "mean"),
            Total_Orders=("Order ID", "nunique")
        ).reset_index().sort_values("Day_Index")

        dow_stats["Revenue_Share_%"] = ((dow_stats["Total_Revenue"] / dow_stats["Total_Revenue"].sum()) * 100).round(2)
        return dow_stats

    @staticmethod
    def get_sales_summary_metrics(df: pd.DataFrame) -> Dict[str, Any]:
        """Extracts peak sales day, best performing month, and sales volatility."""
        daily = SalesAnalytics.get_daily_sales(df)
        monthly = SalesAnalytics.get_monthly_sales(df)

        if daily.empty:
            return {}

        peak_day_row = daily.loc[daily["Revenue"].idxmax()]
        peak_month_row = monthly.loc[monthly["Revenue"].idxmax()] if not monthly.empty else None

        return {
            "peak_day_date": peak_day_row["Order Date"].strftime("%Y-%m-%d"),
            "peak_day_revenue": round(peak_day_row["Revenue"], 2),
            "peak_month": peak_month_row["Year_Month"] if peak_month_row is not None else "N/A",
            "peak_month_revenue": round(peak_month_row["Revenue"], 2) if peak_month_row is not None else 0.0,
            "daily_revenue_mean": round(daily["Revenue"].mean(), 2),
            "daily_revenue_std": round(daily["Revenue"].std(), 2)
        }

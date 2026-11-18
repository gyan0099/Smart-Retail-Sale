"""
Smart Retail Sales Analytics & Visualization System
Profit Analytics Engine
Evaluates Revenue vs Cost, margins, category profitability, and margin leakage.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class ProfitAnalytics:
    """Computes cost dynamics, margin health, and category profitability."""

    @staticmethod
    def get_revenue_vs_cost(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates macro cost, revenue, and gross profit breakdown."""
        if "Revenue" not in df.columns or "Cost" not in df.columns:
            return {}

        total_rev = float(df["Revenue"].sum())
        total_cost = float(df["Cost"].sum())
        total_profit = float(df["Profit"].sum()) if "Profit" in df.columns else (total_rev - total_cost)

        cost_ratio = (total_cost / total_rev * 100) if total_rev > 0 else 0
        profit_margin = (total_profit / total_rev * 100) if total_rev > 0 else 0
        roi_on_cost = (total_profit / total_cost * 100) if total_cost > 0 else 0

        return {
            "total_revenue": round(total_rev, 2),
            "total_cost": round(total_cost, 2),
            "total_profit": round(total_profit, 2),
            "cost_ratio_%": round(cost_ratio, 2),
            "profit_margin_%": round(profit_margin, 2),
            "roi_on_cost_%": round(roi_on_cost, 2)
        }

    @staticmethod
    def get_category_profitability(df: pd.DataFrame) -> pd.DataFrame:
        """Breaks down revenue, cost, profit, and margins by category."""
        if "Category" not in df.columns or "Revenue" not in df.columns or "Cost" not in df.columns:
            return pd.DataFrame()

        cat_prof = df.groupby("Category").agg(
            Revenue=("Revenue", "sum"),
            Cost=("Cost", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Units=("Quantity", "sum")
        ).reset_index()

        cat_prof["Profit_Margin_%"] = ((cat_prof["Profit"] / cat_prof["Revenue"]) * 100).round(2)
        cat_prof["Cost_Share_%"] = ((cat_prof["Cost"] / cat_prof["Revenue"]) * 100).round(2)
        cat_prof["ROI_%"] = ((cat_prof["Profit"] / cat_prof["Cost"]) * 100).round(2)
        return cat_prof.sort_values(by="Profit", ascending=False).reset_index(drop=True)

    @staticmethod
    def get_monthly_profit_trends(df: pd.DataFrame) -> pd.DataFrame:
        """Computes monthly progression of revenue, cost, profit, and margin %."""
        if "Order Date" not in df.columns or "Revenue" not in df.columns:
            return pd.DataFrame()

        df_m = df.copy()
        df_m["Order Date"] = pd.to_datetime(df_m["Order Date"])
        df_m["Year_Month"] = df_m["Order Date"].dt.to_period("M").astype(str)

        m_prof = df_m.groupby("Year_Month").agg(
            Revenue=("Revenue", "sum"),
            Cost=("Cost", "sum"),
            Profit=("Profit", "sum")
        ).reset_index().sort_values("Year_Month")

        m_prof["Profit_Margin_%"] = ((m_prof["Profit"] / m_prof["Revenue"]) * 100).round(2)
        return m_prof

    @staticmethod
    def get_low_margin_items(df: pd.DataFrame, margin_threshold: float = 15.0) -> pd.DataFrame:
        """Identifies products or categories operating under critical margin thresholds."""
        if "Product Name" not in df.columns or "Profit Margin" not in df.columns:
            return pd.DataFrame()

        prod_prof = df.groupby(["Product ID", "Product Name", "Category"]).agg(
            Total_Revenue=("Revenue", "sum"),
            Total_Cost=("Cost", "sum"),
            Total_Profit=("Profit", "sum"),
            Units_Sold=("Quantity", "sum")
        ).reset_index()

        prod_prof["Overall_Margin_%"] = ((prod_prof["Total_Profit"] / prod_prof["Total_Revenue"]) * 100).round(2)
        low_margin = prod_prof[prod_prof["Overall_Margin_%"] < margin_threshold].sort_values("Overall_Margin_%")
        return low_margin.reset_index(drop=True)

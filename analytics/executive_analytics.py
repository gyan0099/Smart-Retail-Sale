"""
Smart Retail Sales Analytics & Visualization System
Executive Analytics Engine
Calculates high-level executive KPIs, growth rates, and health metrics.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

class ExecutiveAnalytics:
    """Computes executive-level business intelligence metrics and KPI cards."""

    @staticmethod
    def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates executive KPIs:
        - Total Revenue
        - Total Profit
        - Total Orders
        - Total Customers
        - Products Sold (Total Quantity)
        - Average Order Value (AOV)
        - Profit Margin (%)
        - Revenue Growth (%) vs prior period
        """
        if df.empty:
            return {
                "total_revenue": 0.0,
                "total_profit": 0.0,
                "total_orders": 0,
                "total_customers": 0,
                "products_sold": 0,
                "avg_order_value": 0.0,
                "profit_margin": 0.0,
                "revenue_growth": 0.0,
                "profit_growth": 0.0,
                "order_growth": 0.0,
                "avg_daily_revenue": 0.0
            }

        total_revenue = float(df["Revenue"].sum()) if "Revenue" in df.columns else 0.0
        total_profit = float(df["Profit"].sum()) if "Profit" in df.columns else 0.0
        total_orders = int(df["Order ID"].nunique()) if "Order ID" in df.columns else len(df)
        total_customers = int(df["Customer ID"].nunique()) if "Customer ID" in df.columns else (
            int(df["Customer Name"].nunique()) if "Customer Name" in df.columns else 0
        )
        products_sold = int(df["Quantity"].sum()) if "Quantity" in df.columns else 0

        avg_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0
        profit_margin = round((total_profit / total_revenue) * 100, 2) if total_revenue > 0 else 0.0

        # Calculate Growth vs Previous Equal Period
        revenue_growth = 0.0
        profit_growth = 0.0
        order_growth = 0.0
        avg_daily_rev = 0.0

        if "Order Date" in df.columns and len(df) > 10:
            df_dates = df.copy()
            df_dates["Order Date"] = pd.to_datetime(df_dates["Order Date"], errors="coerce")
            df_dates = df_dates.dropna(subset=["Order Date"]).sort_values("Order Date")
            
            if not df_dates.empty:
                min_date = df_dates["Order Date"].min()
                max_date = df_dates["Order Date"].max()
                total_days = max(1, (max_date - min_date).days)
                avg_daily_rev = round(total_revenue / total_days, 2)

                # Split data into first half and second half of time window
                mid_date = min_date + (max_date - min_date) / 2
                prior_df = df_dates[df_dates["Order Date"] < mid_date]
                current_df = df_dates[df_dates["Order Date"] >= mid_date]

                prior_rev = prior_df["Revenue"].sum() if "Revenue" in prior_df.columns else 0.0
                curr_rev = current_df["Revenue"].sum() if "Revenue" in current_df.columns else 0.0
                if prior_rev > 0:
                    revenue_growth = round(((curr_rev - prior_rev) / prior_rev) * 100, 2)

                prior_prof = prior_df["Profit"].sum() if "Profit" in prior_df.columns else 0.0
                curr_prof = current_df["Profit"].sum() if "Profit" in current_df.columns else 0.0
                if prior_prof > 0:
                    profit_growth = round(((curr_prof - prior_prof) / prior_prof) * 100, 2)

                prior_orders = prior_df["Order ID"].nunique() if "Order ID" in prior_df.columns else len(prior_df)
                curr_orders = current_df["Order ID"].nunique() if "Order ID" in current_df.columns else len(current_df)
                if prior_orders > 0:
                    order_growth = round(((curr_orders - prior_orders) / prior_orders) * 100, 2)

        return {
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "total_orders": total_orders,
            "total_customers": total_customers,
            "products_sold": products_sold,
            "avg_order_value": avg_order_value,
            "profit_margin": profit_margin,
            "revenue_growth": revenue_growth,
            "profit_growth": profit_growth,
            "order_growth": order_growth,
            "avg_daily_revenue": avg_daily_rev
        }

    @staticmethod
    def get_quick_summary_table(df: pd.DataFrame) -> pd.DataFrame:
        """Generates category-level breakdown for the executive overview."""
        if "Category" not in df.columns:
            return pd.DataFrame()
            
        summary = df.groupby("Category").agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Units_Sold=("Quantity", "sum")
        ).reset_index()

        summary["Profit Margin (%)"] = ((summary["Profit"] / summary["Revenue"]) * 100).round(2)
        summary["Avg Order Value"] = (summary["Revenue"] / summary["Orders"]).round(2)
        summary = summary.sort_values(by="Revenue", ascending=False).reset_index(drop=True)
        return summary

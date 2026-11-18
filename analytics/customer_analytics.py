"""
Smart Retail Sales Analytics & Visualization System
Customer Analytics Engine
RFM Segmentation, Repeat vs New Customers, Purchase Patterns & CLV Estimation.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Tuple

class CustomerAnalytics:
    """Performs customer segmentation, behavioral analysis, and lifetime value estimation."""

    @staticmethod
    def calculate_rfm(df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes Recency, Frequency, and Monetary (RFM) values and assigned segments.
        """
        if "Customer ID" not in df.columns or "Order Date" not in df.columns or "Revenue" not in df.columns:
            return pd.DataFrame()

        df_c = df.copy()
        df_c["Order Date"] = pd.to_datetime(df_c["Order Date"])
        snapshot_date = df_c["Order Date"].max() + pd.Timedelta(days=1)

        rfm = df_c.groupby(["Customer ID", "Customer Name", "Customer Segment"]).agg(
            Recency=("Order Date", lambda x: (snapshot_date - x.max()).days),
            Frequency=("Order ID", "nunique"),
            Monetary=("Revenue", "sum")
        ).reset_index()

        # Score calculations (1-5 scale) using qcut or rank-based bins
        rfm["R_Score"] = pd.qcut(rfm["Recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
        
        # Frequency might have ties, use rank
        rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
        rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

        rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)
        rfm["RFM_Index"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

        # Segment Assignment Logic
        def assign_segment(row):
            r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
            if r >= 4 and f >= 4:
                return "Champions"
            elif r >= 3 and f >= 3:
                return "Loyal Customers"
            elif r >= 4 and f <= 2:
                return "Promising / New"
            elif r <= 2 and f >= 4:
                return "At Risk"
            elif r <= 2 and f <= 2:
                return "Lost / Inactive"
            else:
                return "Potential Loyalists"

        rfm["RFM_Segment"] = rfm.apply(assign_segment, axis=1)
        return rfm

    @staticmethod
    def get_repeat_vs_new(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates proportion and revenue of Repeat vs Single-Purchase (New) customers."""
        if "Customer ID" not in df.columns or "Order ID" not in df.columns:
            return {}

        cust_orders = df.groupby("Customer ID").agg(
            Orders=("Order ID", "nunique"),
            Revenue=("Revenue", "sum")
        ).reset_index()

        repeat_mask = cust_orders["Orders"] > 1
        repeat_count = int(repeat_mask.sum())
        new_count = int((~repeat_mask).sum())
        total_cust = len(cust_orders)

        repeat_rev = float(cust_orders.loc[repeat_mask, "Revenue"].sum())
        new_rev = float(cust_orders.loc[~repeat_mask, "Revenue"].sum())
        total_rev = repeat_rev + new_rev

        return {
            "total_customers": total_cust,
            "repeat_customers": repeat_count,
            "new_customers": new_count,
            "repeat_rate_%": round((repeat_count / total_cust) * 100, 2) if total_cust > 0 else 0,
            "new_rate_%": round((new_count / total_cust) * 100, 2) if total_cust > 0 else 0,
            "repeat_revenue": round(repeat_rev, 2),
            "new_revenue": round(new_rev, 2),
            "repeat_rev_share_%": round((repeat_rev / total_rev) * 100, 2) if total_rev > 0 else 0
        }

    @staticmethod
    def calculate_clv(df: pd.DataFrame, avg_lifespan_years: float = 2.5) -> pd.DataFrame:
        """
        Estimates Customer Lifetime Value (CLV) based on:
        CLV = (Average Order Value) * (Annual Purchase Frequency) * (Gross Margin %) * Lifespan
        """
        rfm = CustomerAnalytics.calculate_rfm(df)
        if rfm.empty:
            return pd.DataFrame()

        # Overall profit margin
        total_rev = df["Revenue"].sum()
        total_profit = df["Profit"].sum()
        overall_margin = (total_profit / total_rev) if total_rev > 0 else 0.25

        # Time span of dataset in years
        dates = pd.to_datetime(df["Order Date"])
        total_years = max(0.5, (dates.max() - dates.min()).days / 365.25)

        clv_df = rfm.copy()
        clv_df["Avg_Order_Value"] = (clv_df["Monetary"] / clv_df["Frequency"]).round(2)
        clv_df["Annual_Purchase_Frequency"] = (clv_df["Frequency"] / total_years).round(2)
        
        # Estimated CLV formula
        clv_df["Estimated_CLV"] = (
            clv_df["Avg_Order_Value"] * 
            clv_df["Annual_Purchase_Frequency"] * 
            overall_margin * 
            avg_lifespan_years
        ).round(2)

        return clv_df.sort_values(by="Estimated_CLV", ascending=False).reset_index(drop=True)

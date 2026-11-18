"""
Smart Retail Sales Analytics & Visualization System
Business Insights & Performance Summary Generator
Generates automated executive insights, anomaly detections, and strategic recommendations.
"""

import pandas as pd
from typing import List, Dict, Any

class InsightsGenerator:
    """Generates rule-based data-driven executive insights and recommendations."""

    @staticmethod
    def generate_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
        """
        Analyzes the dataset and returns a list of actionable business insights.
        """
        if df.empty or len(df) < 5:
            return [{
                "category": "Data Volume",
                "type": "neutral",
                "title": "Insufficient Data",
                "detail": "Please load or filter more data records to compute statistically meaningful insights."
            }]

        insights = []

        # 1. Revenue & Margin Dynamics
        total_rev = df["Revenue"].sum()
        total_profit = df["Profit"].sum()
        margin = (total_profit / total_rev * 100) if total_rev > 0 else 0

        if margin >= 25:
            insights.append({
                "category": "Profitability",
                "type": "positive",
                "title": f"Strong Gross Margin ({margin:.1f}%)",
                "detail": f"Overall gross margin is healthy at {margin:.1f}%, indicating disciplined pricing and resilient supplier cost structures."
            })
        else:
            insights.append({
                "category": "Profitability",
                "type": "warning",
                "title": f"Margin Compression Risk ({margin:.1f}%)",
                "detail": f"Gross margin is currently at {margin:.1f}%. Review high-discount promotional campaigns and low-margin product categories to safeguard bottom-line profitability."
            })

        # 2. Category Performance
        if "Category" in df.columns:
            cat_summary = df.groupby("Category")["Revenue"].sum().sort_values(ascending=False)
            top_cat = cat_summary.index[0]
            top_cat_share = (cat_summary.iloc[0] / total_rev * 100) if total_rev > 0 else 0

            insights.append({
                "category": "Product Portfolio",
                "type": "positive",
                "title": f"Primary Revenue Pillar: {top_cat}",
                "detail": f"'{top_cat}' is the dominant category, generating ₹{cat_summary.iloc[0]:,.2f} ({top_cat_share:.1f}% of total sales). Ensure inventory buffers and marketing efforts prioritize this vertical."
            })

        # 3. Regional Sales Footprint
        if "Region" in df.columns:
            reg_summary = df.groupby("Region")["Revenue"].sum().sort_values(ascending=False)
            top_reg = reg_summary.index[0]
            top_reg_share = (reg_summary.iloc[0] / total_rev * 100) if total_rev > 0 else 0

            insights.append({
                "category": "Geographic Market",
                "type": "positive",
                "title": f"Regional Leader: {top_reg} Zone",
                "detail": f"The {top_reg} region leads all markets with {top_reg_share:.1f}% revenue share. High consumer demand in cities within {top_reg} offers prime opportunities for rapid fulfillment centers."
            })

        # 4. Repeat Customer Retention
        if "Customer ID" in df.columns:
            cust_counts = df.groupby("Customer ID")["Order ID"].nunique()
            repeat_rate = (cust_counts > 1).mean() * 100

            if repeat_rate >= 40:
                insights.append({
                    "category": "Customer Loyalty",
                    "type": "positive",
                    "title": f"High Customer Retention ({repeat_rate:.1f}%)",
                    "detail": f"{repeat_rate:.1f}% of unique customers have placed repeat orders, reflecting strong brand loyalty and recurring lifetime value."
                })
            else:
                insights.append({
                    "category": "Customer Loyalty",
                    "type": "warning",
                    "title": f"Low Repeat Purchase Rate ({repeat_rate:.1f}%)",
                    "detail": f"Repeat purchase rate stands at {repeat_rate:.1f}%. Launch automated re-engagement workflows and loyalty rewards programs to increase order frequency."
                })

        # 5. Payment Preference
        if "Payment Method" in df.columns:
            pm_counts = df["Payment Method"].value_counts(normalize=True) * 100
            top_pm = pm_counts.index[0]
            insights.append({
                "category": "Payment Operations",
                "type": "neutral",
                "title": f"Preferred Channel: {top_pm} ({pm_counts.iloc[0]:.1f}%)",
                "detail": f"Customers overwhelmingly prefer '{top_pm}' checkout. Ensure payment gateway redundancy and 0% checkout drop-off rates for this method."
            })

        return insights

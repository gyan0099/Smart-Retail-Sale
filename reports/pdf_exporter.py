"""
Smart Retail Sales Analytics & Visualization System
Executive PDF Report Generator
Generates high-resolution multi-page PDF reports using matplotlib.backends.backend_pdf.
"""

import io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime

class PDFReportExporter:
    """Generates publication-quality multi-page executive PDF reports."""

    @staticmethod
    def generate_pdf_report(df: pd.DataFrame) -> bytes:
        """
        Builds a multi-page PDF report containing:
        - Cover & Executive KPI Overview
        - Monthly Trends & Performance
        - Category & Product Breakdown
        - Regional & Customer Distribution
        """
        pdf_buffer = io.BytesIO()
        plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

        # Color constants
        primary_color = "#1E3A8A"
        secondary_color = "#3B82F6"
        accent_color = "#10B981"
        gray_color = "#64748B"

        with PdfPages(pdf_buffer) as pdf:
            # ---------------- PAGE 1: EXECUTIVE OVERVIEW ----------------
            fig1 = plt.figure(figsize=(8.27, 11.69)) # Standard A4
            
            # Header Block
            plt.subplot2grid((6, 2), (0, 0), colspan=2)
            plt.axis("off")
            plt.text(0.5, 0.75, "SMART RETAIL SALES ANALYTICS & VISUALIZATION", 
                     fontsize=15, fontweight="bold", ha="center", color=primary_color)
            plt.text(0.5, 0.50, "Executive Business Intelligence Performance Report", 
                     fontsize=11, ha="center", color=secondary_color, fontweight="semibold")
            plt.text(0.5, 0.25, f"SR UNIVERSITY • School of CS & AI • Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                     fontsize=8.5, ha="center", color=gray_color)
            plt.axhline(y=0.1, color=primary_color, linewidth=2)

            # KPI Summary Table
            total_rev = df["Revenue"].sum() if "Revenue" in df.columns else 0
            total_cost = df["Cost"].sum() if "Cost" in df.columns else 0
            total_prof = df["Profit"].sum() if "Profit" in df.columns else 0
            margin = (total_prof / total_rev * 100) if total_rev > 0 else 0
            orders = df["Order ID"].nunique() if "Order ID" in df.columns else len(df)
            custs = df["Customer ID"].nunique() if "Customer ID" in df.columns else 0
            aov = (total_rev / orders) if orders > 0 else 0

            plt.subplot2grid((6, 2), (1, 0), colspan=2)
            plt.axis("off")
            kpi_data = [
                ["Total Revenue", f"Rs. {total_rev:,.2f}", "Total Orders", f"{orders:,}"],
                ["Total Gross Profit", f"Rs. {total_prof:,.2f}", "Unique Customers", f"{custs:,}"],
                ["Profit Margin", f"{margin:.2f}%", "Avg Order Value (AOV)", f"Rs. {aov:,.2f}"]
            ]
            table = plt.table(cellText=kpi_data, colLabels=["Metric", "Value", "Metric", "Value"], 
                              cellLoc="center", loc="center", colColours=["#E2E8F0", "#F1F5F9", "#E2E8F0", "#F1F5F9"])
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.8)

            # Monthly Trend Chart
            if "Order Date" in df.columns and "Revenue" in df.columns:
                plt.subplot2grid((6, 2), (2, 0), rowspan=2, colspan=2)
                df_temp = df.copy()
                df_temp["Month"] = pd.to_datetime(df_temp["Order Date"]).dt.to_period("M").astype(str)
                monthly = df_temp.groupby("Month").agg({"Revenue": "sum", "Profit": "sum"}).reset_index()
                
                plt.plot(monthly["Month"], monthly["Revenue"] / 1000, marker="o", color=primary_color, label="Revenue (k)")
                plt.plot(monthly["Month"], monthly["Profit"] / 1000, marker="s", color=accent_color, label="Profit (k)")
                plt.title("Monthly Revenue & Profit Progression", fontsize=11, fontweight="bold", pad=8)
                plt.xlabel("Month", fontsize=8)
                plt.ylabel("Amount (Rs. '000)", fontsize=8)
                plt.xticks(rotation=45, fontsize=7)
                plt.yticks(fontsize=7)
                plt.legend(fontsize=8)
                plt.grid(True, linestyle="--", alpha=0.5)

            # Category Revenue Pie / Donut
            if "Category" in df.columns:
                plt.subplot2grid((6, 2), (4, 0), rowspan=2)
                cat_sales = df.groupby("Category")["Revenue"].sum()
                plt.pie(cat_sales, labels=cat_sales.index, autopct="%1.1f%%", startangle=140, 
                        colors=["#1E3A8A", "#3B82F6", "#0D9488", "#10B981", "#F59E0B", "#EF4444"],
                        textprops={'fontsize': 7})
                plt.title("Revenue Share by Category", fontsize=10, fontweight="bold")

            # Regional Revenue Bar
            if "Region" in df.columns:
                plt.subplot2grid((6, 2), (4, 1), rowspan=2)
                reg_sales = df.groupby("Region")["Revenue"].sum().sort_values()
                plt.barh(reg_sales.index, reg_sales.values / 1000, color=secondary_color)
                plt.title("Regional Revenue (Rs. '000)", fontsize=10, fontweight="bold")
                plt.xlabel("Revenue (Rs. '000)", fontsize=8)
                plt.xticks(fontsize=7)
                plt.yticks(fontsize=8)
                plt.grid(True, linestyle="--", alpha=0.5)

            plt.tight_layout()
            pdf.savefig(fig1)
            plt.close(fig1)

            # ---------------- PAGE 2: STRATEGIC INSIGHTS ----------------
            fig2 = plt.figure(figsize=(8.27, 11.69))
            
            plt.subplot2grid((6, 1), (0, 0))
            plt.axis("off")
            plt.text(0.05, 0.7, "STRATEGIC BUSINESS INSIGHTS & ACTION PLAN", 
                     fontsize=14, fontweight="bold", color=primary_color)
            plt.text(0.05, 0.35, "Actionable findings derived from predictive & historical retail analytics", 
                     fontsize=10, color=gray_color)
            plt.axhline(y=0.1, color=primary_color, linewidth=1.5)

            # Top 10 Products Table
            if "Product Name" in df.columns:
                plt.subplot2grid((6, 1), (1, 0), rowspan=3)
                plt.axis("off")
                top_prods = df.groupby(["Product Name", "Category"]).agg(
                    Rev=("Revenue", "sum"),
                    Prof=("Profit", "sum"),
                    Qty=("Quantity", "sum")
                ).reset_index().sort_values("Rev", ascending=False).head(10)

                table_data = []
                for _, r in top_prods.iterrows():
                    table_data.append([
                        r["Product Name"][:28],
                        r["Category"],
                        f"{r['Qty']:,}",
                        f"Rs. {r['Rev']:,.0f}",
                        f"Rs. {r['Prof']:,.0f}",
                        f"{(r['Prof']/r['Rev']*100):.1f}%"
                    ])

                prod_table = plt.table(
                    cellText=table_data,
                    colLabels=["Product", "Category", "Units", "Revenue", "Profit", "Margin"],
                    cellLoc="center",
                    loc="center",
                    colColours=["#E2E8F0"]*6
                )
                prod_table.auto_set_font_size(False)
                prod_table.set_fontsize(7.5)
                prod_table.scale(1, 1.5)
                plt.title("Top 10 Revenue Generating Products", fontsize=11, fontweight="bold", pad=12)

            # Recommendations text
            plt.subplot2grid((6, 1), (4, 0), rowspan=2)
            plt.axis("off")
            recs = (
                "KEY STRATEGIC RECOMMENDATIONS:\n\n"
                "1. High Margin Category Expansion:\n"
                "   Focus promotional campaigns on high-margin product verticals while controlling discounts.\n\n"
                "2. Customer Retention & RFM Workflows:\n"
                "   Engage 'At-Risk' customer segments with targeted retention offers and loyalty incentives.\n\n"
                "3. Regional Inventory Optimization:\n"
                "   Establish fulfillment hubs in top-performing regions to minimize delivery latency and shipping costs.\n\n"
                "4. Demand-Driven Restocking:\n"
                "   Leverage machine learning demand forecasts to align inventory replenishment with seasonal demand spikes."
            )
            plt.text(0.05, 0.90, recs, fontsize=9.5, verticalalignment="top", linespacing=1.4, color="#1E293B")

            plt.tight_layout()
            pdf.savefig(fig2)
            plt.close(fig2)

        return pdf_buffer.getvalue()

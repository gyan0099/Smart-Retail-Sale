"""
Smart Retail Sales Analytics & Visualization System
Multi-Sheet Excel Report Exporter
Generates professional formatted Excel workbooks with KPIs, clean data, and analytical summaries.
"""

import io
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class ExcelReportExporter:
    """Creates polished multi-tab Excel reports from retail analytics data."""

    @staticmethod
    def generate_excel_report(df: pd.DataFrame) -> bytes:
        """
        Builds a multi-sheet Excel workbook containing:
        - Executive Summary (KPI cards & metrics)
        - Cleaned Sales Data
        - Monthly Trends
        - Category Performance
        - Regional Performance
        - Top Products
        """
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            wb = writer.book

            # Palette styles
            header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
            header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            sub_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
            bold_font = Font(name="Calibri", size=11, bold=True)
            border_thin = Border(
                left=Side(style='thin', color='E2E8F0'),
                right=Side(style='thin', color='E2E8F0'),
                top=Side(style='thin', color='E2E8F0'),
                bottom=Side(style='thin', color='E2E8F0')
            )

            # --- Sheet 1: Executive Summary ---
            ws_summary = wb.create_sheet(title="Executive_Summary", index=0)
            ws_summary.views.sheetView[0].showGridLines = True

            # Title Header
            ws_summary.merge_cells("A1:E1")
            ws_summary["A1"] = "SMART RETAIL SALES ANALYTICS - EXECUTIVE SUMMARY"
            ws_summary["A1"].font = Font(name="Calibri", size=14, bold=True, color="1E3A8A")

            ws_summary.merge_cells("A2:E2")
            ws_summary["A2"] = "SR University • Data Analytics and Visualization (25CAI202PC201)"
            ws_summary["A2"].font = Font(name="Calibri", size=10, italic=True, color="64748B")

            # KPI Block
            total_rev = float(df["Revenue"].sum()) if "Revenue" in df.columns else 0.0
            total_cost = float(df["Cost"].sum()) if "Cost" in df.columns else 0.0
            total_prof = float(df["Profit"].sum()) if "Profit" in df.columns else 0.0
            margin = (total_prof / total_rev * 100) if total_rev > 0 else 0.0
            orders = int(df["Order ID"].nunique()) if "Order ID" in df.columns else len(df)
            custs = int(df["Customer ID"].nunique()) if "Customer ID" in df.columns else 0
            units = int(df["Quantity"].sum()) if "Quantity" in df.columns else 0
            aov = (total_rev / orders) if orders > 0 else 0.0

            kpis = [
                ("Total Revenue", f"₹{total_rev:,.2f}"),
                ("Total Cost", f"₹{total_cost:,.2f}"),
                ("Total Profit", f"₹{total_prof:,.2f}"),
                ("Profit Margin", f"{margin:.2f}%"),
                ("Total Orders", f"{orders:,}"),
                ("Total Unique Customers", f"{custs:,}"),
                ("Total Products Sold (Units)", f"{units:,}"),
                ("Average Order Value (AOV)", f"₹{aov:,.2f}")
            ]

            ws_summary.cell(row=4, column=1, value="Key Performance Indicator").font = header_font
            ws_summary.cell(row=4, column=1).fill = header_fill
            ws_summary.cell(row=4, column=2, value="Metric Value").font = header_font
            ws_summary.cell(row=4, column=2).fill = header_fill

            for idx, (label, val) in enumerate(kpis, start=5):
                ws_summary.cell(row=idx, column=1, value=label).font = Font(name="Calibri", size=11)
                ws_summary.cell(row=idx, column=2, value=val).font = bold_font
                ws_summary.cell(row=idx, column=1).border = border_thin
                ws_summary.cell(row=idx, column=2).border = border_thin

            ws_summary.column_dimensions["A"].width = 32
            ws_summary.column_dimensions["B"].width = 24

            # --- Sheet 2: Category Breakdown ---
            if "Category" in df.columns:
                cat_df = df.groupby("Category").agg(
                    Revenue=("Revenue", "sum"),
                    Cost=("Cost", "sum"),
                    Profit=("Profit", "sum"),
                    Units=("Quantity", "sum"),
                    Orders=("Order ID", "nunique")
                ).reset_index()
                cat_df["Profit Margin %"] = ((cat_df["Profit"] / cat_df["Revenue"]) * 100).round(2)
                cat_df.to_excel(writer, sheet_name="Category_Analysis", index=False)

            # --- Sheet 3: Regional Breakdown ---
            if "Region" in df.columns:
                reg_df = df.groupby(["Region", "State"]).agg(
                    Revenue=("Revenue", "sum"),
                    Profit=("Profit", "sum"),
                    Units=("Quantity", "sum")
                ).reset_index()
                reg_df["Profit Margin %"] = ((reg_df["Profit"] / reg_df["Revenue"]) * 100).round(2)
                reg_df.to_excel(writer, sheet_name="Regional_Analysis", index=False)

            # --- Sheet 4: Monthly Trend ---
            if "Order Date" in df.columns and "Revenue" in df.columns:
                df_temp = df.copy()
                df_temp["Month"] = pd.to_datetime(df_temp["Order Date"]).dt.to_period("M").astype(str)
                monthly = df_temp.groupby("Month").agg(
                    Revenue=("Revenue", "sum"),
                    Profit=("Profit", "sum"),
                    Orders=("Order ID", "nunique")
                ).reset_index()
                monthly.to_excel(writer, sheet_name="Monthly_Trends", index=False)

            # --- Sheet 5: Top Products ---
            if "Product Name" in df.columns:
                prod_df = df.groupby(["Product Name", "Category"]).agg(
                    Revenue=("Revenue", "sum"),
                    Profit=("Profit", "sum"),
                    Units_Sold=("Quantity", "sum")
                ).reset_index().sort_values(by="Revenue", ascending=False).head(50)
                prod_df.to_excel(writer, sheet_name="Top_50_Products", index=False)

            # --- Sheet 6: Full Data ---
            df.head(5000).to_excel(writer, sheet_name="Cleaned_Sales_Data", index=False)

            # Style each table sheet header
            for sheet in wb.sheetnames:
                if sheet == "Executive_Summary":
                    continue
                ws = wb[sheet]
                ws.views.sheetView[0].showGridLines = True
                for cell in ws[1]:
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                # Auto-fit columns
                for col in ws.columns:
                    max_len = max(len(str(cell.value or '')) for cell in col)
                    col_letter = get_column_letter(col[0].column)
                    ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        return output.getvalue()

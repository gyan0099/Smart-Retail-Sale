"""
Smart Retail Sales Analytics & Visualization System
Generates high-resolution figures for academic report and asset gallery.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import ASSETS_DIR
from data.data_manager import DataManager

def generate_academic_figures():
    """Generates the 6 formal figures required by the university template."""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    df = DataManager.load_default_sample()
    
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    colors = ["#1E3A8A", "#3B82F6", "#0D9488", "#10B981", "#F59E0B", "#EF4444"]

    # 1. Figure 5.1: Monthly Sales & Profit Trend
    plt.figure(figsize=(9, 4.5), dpi=200)
    df_temp = df.copy()
    df_temp["Month"] = pd.to_datetime(df_temp["Order Date"]).dt.to_period("M").astype(str)
    monthly = df_temp.groupby("Month").agg({"Revenue": "sum", "Profit": "sum"}).reset_index()
    
    plt.plot(monthly["Month"], monthly["Revenue"] / 1000, marker="o", linewidth=2.5, color="#1E3A8A", label="Revenue (₹ '000)")
    plt.plot(monthly["Month"], monthly["Profit"] / 1000, marker="s", linewidth=2.5, color="#10B981", label="Profit (₹ '000)")
    plt.title("Figure 5.1: Monthly Sales and Gross Profit Progression (2024 - 2026)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Timeline (Year-Month)", fontsize=10, fontweight="semibold")
    plt.ylabel("Amount (₹ in Thousands)", fontsize=10, fontweight="semibold")
    plt.xticks(rotation=45, fontsize=8)
    plt.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0")
    plt.tight_layout()
    fig1_path = os.path.join(ASSETS_DIR, "figure_5_1_monthly_trend.png")
    plt.savefig(fig1_path)
    plt.close()
    print("Saved:", fig1_path)

    # 2. Figure 5.2: Category-wise Revenue & Profit Margin
    plt.figure(figsize=(9, 4.5), dpi=200)
    cat_df = df.groupby("Category").agg({"Revenue": "sum", "Profit": "sum"}).reset_index().sort_values("Revenue", ascending=False)
    x = np.arange(len(cat_df))
    width = 0.38
    
    plt.bar(x - width/2, cat_df["Revenue"] / 1000, width, label="Revenue (₹ '000)", color="#3B82F6")
    plt.bar(x + width/2, cat_df["Profit"] / 1000, width, label="Profit (₹ '000)", color="#0D9488")
    plt.title("Figure 5.2: Category-wise Revenue and Profit Comparison", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Product Category", fontsize=10, fontweight="semibold")
    plt.ylabel("Amount (₹ in Thousands)", fontsize=10, fontweight="semibold")
    plt.xticks(x, cat_df["Category"], rotation=20, fontsize=8, ha="right")
    plt.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0")
    plt.tight_layout()
    fig2_path = os.path.join(ASSETS_DIR, "figure_5_2_category_performance.png")
    plt.savefig(fig2_path)
    plt.close()
    print("Saved:", fig2_path)

    # 3. Figure 5.3: Regional Sales Distribution
    plt.figure(figsize=(7, 5), dpi=200)
    reg_df = df.groupby("Region")["Revenue"].sum().sort_values(ascending=False)
    wedges, texts, autotexts = plt.pie(
        reg_df, labels=reg_df.index, autopct="%1.1f%%", startangle=140,
        colors=colors[:len(reg_df)],
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_fontweight("bold")
    plt.title("Figure 5.3: Regional Sales Contribution Share", fontsize=12, fontweight="bold", pad=12)
    plt.tight_layout()
    fig3_path = os.path.join(ASSETS_DIR, "figure_5_3_regional_share.png")
    plt.savefig(fig3_path)
    plt.close()
    print("Saved:", fig3_path)

    # 4. Figure 5.4: Customer RFM Segmentation
    from analytics.customer_analytics import CustomerAnalytics
    rfm = CustomerAnalytics.calculate_rfm(df)
    plt.figure(figsize=(8, 4.5), dpi=200)
    seg_counts = rfm["RFM_Segment"].value_counts()
    plt.barh(seg_counts.index, seg_counts.values, color="#6366F1")
    plt.title("Figure 5.4: Customer RFM Behavioral Segmentation Distribution", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Number of Customers", fontsize=10, fontweight="semibold")
    plt.ylabel("Customer Segment", fontsize=10, fontweight="semibold")
    plt.tight_layout()
    fig4_path = os.path.join(ASSETS_DIR, "figure_5_4_rfm_segments.png")
    plt.savefig(fig4_path)
    plt.close()
    print("Saved:", fig4_path)

    # 5. Figure 5.5: Future Sales Forecasting Model
    from machine_learning.forecasting import SalesForecaster
    forecast_df, _ = SalesForecaster.forecast_sales(df, days_ahead=45)
    plt.figure(figsize=(9, 4.5), dpi=200)
    actual_data = forecast_df[forecast_df["Data_Type"] == "Actual"].tail(90)
    pred_data = forecast_df[forecast_df["Data_Type"] == "Forecast (Predicted)"]
    
    plt.plot(pd.to_datetime(actual_data["Order Date"]), actual_data["Revenue"] / 1000, 
             label="Actual Historical Sales (₹ '000)", color="#1E3A8A", linewidth=2)
    plt.plot(pd.to_datetime(pred_data["Order Date"]), pred_data["Revenue"] / 1000, 
             label="ML Forecast (Predicted) (₹ '000)", color="#F59E0B", linewidth=2.5, linestyle="--")
    plt.fill_between(
        pd.to_datetime(pred_data["Order Date"]),
        pred_data["Lower_Bound"] / 1000,
        pred_data["Upper_Bound"] / 1000,
        color="#F59E0B", alpha=0.2, label="80% Prediction Interval"
    )
    plt.title("Figure 5.5: Machine Learning Sales Forecast: Historical vs. Predicted", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Date", fontsize=10, fontweight="semibold")
    plt.ylabel("Sales Volume (₹ in Thousands)", fontsize=10, fontweight="semibold")
    plt.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0")
    plt.xticks(rotation=30)
    plt.tight_layout()
    fig5_path = os.path.join(ASSETS_DIR, "figure_5_5_ml_forecast.png")
    plt.savefig(fig5_path)
    plt.close()
    print("Saved:", fig5_path)

    # 6. Figure 5.6: Revenue vs Cost Scatter
    plt.figure(figsize=(8, 4.5), dpi=200)
    plt.scatter(df["Cost"], df["Revenue"], alpha=0.6, color="#0D9488", edgecolors="none")
    plt.plot([0, df["Cost"].max()], [0, df["Cost"].max()], linestyle="--", color="#EF4444", label="Breakeven Line (Rev=Cost)")
    plt.title("Figure 5.6: Revenue vs. Cost Distribution Across Orders", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Order Cost (₹)", fontsize=10, fontweight="semibold")
    plt.ylabel("Order Revenue (₹)", fontsize=10, fontweight="semibold")
    plt.legend()
    plt.tight_layout()
    fig6_path = os.path.join(ASSETS_DIR, "figure_5_6_rev_vs_cost.png")
    plt.savefig(fig6_path)
    plt.close()
    print("Saved:", fig6_path)

if __name__ == "__main__":
    generate_academic_figures()

# Smart Retail Sales Analytics & Visualization System

**Course:** Data Analytics and Visualization (25CAI202PC201)  
**Institution:** SR University, Warangal, Telangana  
**Department:** School of Computer Science and Artificial Intelligence  
**Academic Year:** 2026-27  

---

## 📌 Executive Overview
The **Smart Retail Sales Analytics & Visualization System** is an enterprise-grade Business Intelligence (BI) and Predictive Analytics web application engineered using **Python, Streamlit, Plotly, Scikit-learn, and SQLite**. The system transforms multi-channel retail transactional data into dynamic operational KPIs, interactive multi-dimensional visualizations, algorithmic behavioral segmentations, and machine learning sales forecasts.

---

## 🛠️ Technology Stack
- **Web Interface:** [Streamlit](https://streamlit.io/)
- **Data Engineering:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Interactive Visualizations:** [Plotly](https://plotly.com/python/) (Line, Bar, Donut, Area, Heatmap, Scatter, Geo Map)
- **Machine Learning:** [Scikit-learn](https://scikit-learn.org/) (Ridge Regression, Random Forest, K-Means Clustering, PCA)
- **Database:** [SQLite3](https://www.sqlite.org/) (Persistent logging, active sales tables, audit trail, snapshots)
- **Reporting Engine:** [OpenPyXL](https://openpyxl.readthedocs.io/) (Multi-tab Excel workbooks), [Matplotlib](https://matplotlib.org/) (Vector PDF reports), [python-docx](https://python-docx.readthedocs.io/) (Official university report)

---

## 📁 Project Architecture & Folder Structure

```
dav project/
│
├── app.py                            # Main Streamlit Web Application Entrypoint
├── config.py                         # App metadata, theme palettes, geo coordinates
├── requirements.txt                  # Full list of Python dependencies
├── README.md                         # Project documentation and execution instructions
│
├── data/
│   ├── sample_generator.py           # Realistic retail sales data generator (3,650 orders)
│   ├── retail_sales_sample.csv       # Pre-generated sample retail sales data
│   ├── retail_sales_sample.xlsx      # Excel version of retail sales data
│   └── data_manager.py               # Ingestion, validation, missing value imputation, type coercion
│
├── database/
│   ├── db_manager.py                 # SQLite database schema, upload registry, audit logging
│   └── retail_analytics.db           # SQLite database file
│
├── analytics/
│   ├── executive_analytics.py        # Executive KPIs, AOV, margins, period growth
│   ├── sales_analytics.py            # Daily, monthly, yearly trends, seasonality
│   ├── product_analytics.py          # Top/bottom products, category margins, Pareto analysis
│   ├── customer_analytics.py         # RFM segmentation, repeat vs new, CLV estimates
│   ├── regional_analytics.py         # Regional comparison, city coordinates, spatial aggregation
│   └── profit_analytics.py           # Revenue vs Cost, profit margins, low-margin monitors
│
├── machine_learning/
│   ├── forecasting.py                # Ridge Regression time-series forecasting + confidence intervals
│   ├── demand_prediction.py          # Random Forest demand prediction + What-If scenario simulator
│   └── customer_clustering.py        # Unsupervised K-Means clustering + PCA 2D projections
│
├── components/
│   ├── ui_cards.py                   # Custom HTML KPI metric cards with delta indicators
│   ├── sidebar.py                    # Multi-page navigation & global dynamic filters
│   └── visualizer.py                 # Interactive Plotly chart builders
│
├── reports/
│   ├── excel_exporter.py             # Multi-sheet Excel workbook generator
│   ├── pdf_exporter.py               # Vector multi-page PDF generator
│   ├── insights_generator.py         # Algorithmic business insights & recommendations
│   └── generate_report_charts.py     # Script generating figures for the academic report
│
├── assets/
│   ├── style.css                     # Custom enterprise CSS styling
│   └── figure_5_*.png                # High-resolution academic report figures
│
└── templates/
    ├── academic_project_report.docx  # Official SR University Project Report (.docx)
    └── academic_project_report.md    # University Report in Markdown format
```

---

## 🚀 Key Modules & Capabilities

1. **Executive Dashboard:** Total Revenue, Total Profit, Total Orders, Total Customers, Products Sold, Average Order Value (AOV), Profit Margin, Revenue Growth (Period-over-Period), and interactive snapshot saving.
2. **Sales Analytics:** Daily sales with 7-day rolling moving average, cumulative revenue trajectory, Monthly trends with MoM growth rates, Yearly YoY comparison, and Day of Week revenue decomposition.
3. **Product Analytics:** Top 10 best-selling & bottom 10 products, Category-wise revenue, Sub-category breakdown, and Pareto (80/20) revenue concentration analysis.
4. **Customer Analytics:** RFM (Recency, Frequency, Monetary) behavioral scoring, Repeat vs. Single-Purchase Customer ratios, and estimated Customer Lifetime Value (CLV).
5. **Regional Analytics:** Performance by Zone (North, South, East, West, Central), State-level breakdown, Top 15 Cities ranking, and an interactive Plotly Indian Geospatial Bubble Map.
6. **Profit Analytics:** Revenue vs. Cost of Goods Sold (COGS), Category-wise margin breakdowns, Monthly margin expansion/compression, and an automated low-margin item detector.
7. **Machine Learning:**
   - **Sales Forecasting:** Ridge Regression with seasonal lag features, forecasting up to 90 days with 80% confidence intervals and evaluation metrics (MAE, RMSE, MAPE %, R²).
   - **Demand Prediction:** Supervised Random Forest Regressor predicting order quantities with an interactive **What-If Scenario Simulator**.
   - **Customer Clustering:** Unsupervised K-Means clustering on RFM vectors with Silhouette evaluation and 2D PCA projection.
8. **Data Management:** File uploader supporting CSV and Excel (`.xlsx`, `.xls`), column schema validation, null value detector, duplicate cleaner, IQR outlier inspection, and cleaned dataset export.
9. **Interactive Visualization:** 8 Plotly chart types (Line, Bar, Pie, Donut, Area, Heatmap, Scatter, Geo Map).
10. **Report Generation:** Downloadable multi-page vector PDF reports, multi-tab Excel workbooks, and automated business insights.
11. **Academic Report (SR University):** Full official report formatted according to the SR University DAV course template, with downloadable Word (`.docx`) and Markdown (`.md`) files.

---

## ⚡ Quick Start & Local Execution

### 1. Prerequisites
Ensure Python 3.10+ is installed on your workstation.

### 2. Install Dependencies
Open PowerShell or Terminal in the project directory and run:
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```

The application will launch automatically in your browser at `http://localhost:8501`.

---

## 🎓 Academic Report Details
The project includes a formal academic report written strictly following the SR University template:
- **Title Page:** SR University, School of CS & AI, Warangal, Course: 25CAI202PC201, Academic Year 2026-27.
- **Certificate:** Bonafide record certificate with Faculty Signature and Date fields.
- **Chapters:**
  - Chapter 1: Project Goal (Problem Statement, Objectives, Questions)
  - Chapter 2: Data Overview (Attributes, Data Types, Target Variables)
  - Chapter 3: Data Cleaning Process (Missing values, Duplicates, Types, Outliers, Standardization)
  - Chapter 4: Data Analysis (Descriptive Statistics, EDA, Key Findings)
  - Chapter 5: Visualisation (Figures 5.1 through 5.6 with captions and conclusions + Dashboard)
  - Chapter 6: Final Conclusion (Objective answers, Practical business value)
  - Chapter 7: Future Outcomes and Limitations
  - Appendix: Code and Execution Instructions
- **Downloadable Word Document:** [academic_project_report.docx](templates/academic_project_report.docx)
